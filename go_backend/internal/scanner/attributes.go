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
    Resolution      int
    Bitrate         int
    FilesizeMB      float64
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
            CodecType   string `json:"codec_type"`
            Height      int    `json:"height"`
            RFrameRate  string `json:"r_frame_rate"`
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
        if s.CodecType != "video" {
            continue
        }
        attrs.Resolution = s.Height
        attrs.FPS = parseFrameRate(s.RFrameRate)
        break
    }

    return attrs, nil
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
