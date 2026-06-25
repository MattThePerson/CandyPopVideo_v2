package scanner

import (
    "encoding/json"
    "fmt"
    "math"
    "os/exec"
    "strconv"
    "strings"
)

type VideoAttributes struct {
    DurationSeconds float64
    Duration        string
    FPS             float64
    Height          int
    Width           int
    Resolution      string // "1920x1080"
    AspectRatio     string // "16:9"
    Bitrate         int
    FilesizeMB      float64
    IsVFR           bool
    VideoCodec      string
    AudioCodec      string
    PixFmt          string
    ColorTransfer   string
}

// ProbeAttributes runs ffprobe on the given path and returns video attributes.
func ProbeAttributes(path string) (VideoAttributes, error) {
    out, err := exec.Command(
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        path,
    ).Output()
    if err != nil {
        return VideoAttributes{}, fmt.Errorf("ffprobe: %w", err)
    }

    var probe struct {
        Streams []struct {
            CodecType          string `json:"codec_type"`
            CodecName          string `json:"codec_name"`
            Height             int    `json:"height"`
            Width              int    `json:"width"`
            RFrameRate         string `json:"r_frame_rate"`
            AvgFrameRate       string `json:"avg_frame_rate"`
            DisplayAspectRatio string `json:"display_aspect_ratio"`
            PixFmt             string `json:"pix_fmt"`
            ColorTransfer      string `json:"color_transfer"`
        } `json:"streams"`
        Format struct {
            Duration string `json:"duration"`
            Size     string `json:"size"`
            BitRate  string `json:"bit_rate"`
        } `json:"format"`
    }
    if err := json.Unmarshal(out, &probe); err != nil {
        return VideoAttributes{}, fmt.Errorf("ffprobe parse: %w", err)
    }

    var attrs VideoAttributes

    if d, err := strconv.ParseFloat(probe.Format.Duration, 64); err == nil {
        attrs.DurationSeconds = d
        attrs.Duration = formatDuration(d)
    }
    if sz, err := strconv.ParseInt(probe.Format.Size, 10, 64); err == nil {
        attrs.FilesizeMB = float64(sz) / 1024 / 1024
    }
    if br, err := strconv.ParseInt(probe.Format.BitRate, 10, 64); err == nil {
        attrs.Bitrate = int(br / 1000) // bits/s → kbps
    }

    for _, s := range probe.Streams {
        switch s.CodecType {
        case "video":
            if attrs.Height != 0 {
                continue
            }
            attrs.Height = s.Height
            attrs.Width = s.Width
            attrs.FPS = parseFrameRate(s.RFrameRate)
            attrs.IsVFR = detectVFR(s.RFrameRate, s.AvgFrameRate)
            attrs.VideoCodec = s.CodecName
            attrs.PixFmt = s.PixFmt
            attrs.ColorTransfer = s.ColorTransfer
            attrs.AspectRatio = s.DisplayAspectRatio
            if attrs.AspectRatio == "" || attrs.AspectRatio == "0:1" {
                attrs.AspectRatio = computeAspectRatio(s.Width, s.Height)
            }
            if s.Width > 0 && s.Height > 0 {
                attrs.Resolution = fmt.Sprintf("%dx%d", s.Width, s.Height)
            }
        case "audio":
            if attrs.AudioCodec == "" {
                attrs.AudioCodec = s.CodecName
            }
        }
    }

    return attrs, nil
}

// detectVFR returns true when r_frame_rate and avg_frame_rate differ by more
// than 1%. Good heuristic for VFR content; a single dropped frame in a CFR
// file can also trigger it. For certainty, sample packet durations instead.
func detectVFR(rFrameRate, avgFrameRate string) bool {
    rfps := parseFrameRate(rFrameRate)
    afps := parseFrameRate(avgFrameRate)
    if rfps == 0 || afps == 0 {
        return false
    }
    return math.Abs(rfps-afps)/rfps > 0.01
}

func computeAspectRatio(w, h int) string {
    if w == 0 || h == 0 {
        return ""
    }
    g := gcd(w, h)
    return fmt.Sprintf("%d:%d", w/g, h/g)
}

func gcd(a, b int) int {
    for b != 0 {
        a, b = b, a%b
    }
    return a
}

// parseFrameRate evaluates a fraction string like "30000/1001" → 29.97.
func parseFrameRate(s string) float64 {
    parts := strings.SplitN(s, "/", 2)
    if len(parts) != 2 {
        f, _ := strconv.ParseFloat(s, 64)
        return f
    }
    num, err1 := strconv.ParseFloat(parts[0], 64)
    den, err2 := strconv.ParseFloat(parts[1], 64)
    if err1 != nil || err2 != nil || den == 0 {
        return 0
    }
    return math.Round(num/den*100) / 100
}

// formatDuration converts seconds to "HH:MM:SS" (always zero-padded) so
// direct string comparison matches chronological order.
func formatDuration(secs float64) string {
    total := int(secs)
    h := total / 3600
    m := (total % 3600) / 60
    s := total % 60
    return fmt.Sprintf("%02d:%02d:%02d", h, m, s)
}
