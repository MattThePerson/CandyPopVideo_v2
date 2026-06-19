package mediagen

import (
    "encoding/json"
    "fmt"
    "math"
    "os"
    "os/exec"
    "path/filepath"
    "strconv"
    "strings"
    "sync"
)

// GenerateSpritesheet generates {stem}.jpg (tiled spritesheet) and {stem}.vtt in outDir.
// nFrames=16 for teaser thumbs, 400 for seek thumbs. height=300 for both.
// workers controls how many ffmpeg processes run concurrently for frame extraction.
func GenerateSpritesheet(videoPath, outDir, stem string, nFrames, height, workers int) error {
    vidW, vidH, duration, err := probeVideoInfo(videoPath)
    if err != nil {
        return fmt.Errorf("probe: %w", err)
    }

    thumbW := int(float64(height) * float64(vidW) / float64(vidH))
    cols := int(math.Ceil(math.Sqrt(float64(nFrames))))
    rows := int(math.Ceil(float64(nFrames) / float64(cols)))
    interval := duration / float64(nFrames)

    if err := os.MkdirAll(outDir, 0755); err != nil {
        return err
    }
    tmpDir := filepath.Join(outDir, "tmp_"+stem)
    if err := os.MkdirAll(tmpDir, 0755); err != nil {
        return err
    }
    defer os.RemoveAll(tmpDir)

    // Step 1: extract N frames with fast input-level seek.
    // -ss before -i jumps to the nearest keyframe without decoding the whole video.
    // Worker pool: exactly workers goroutines pull frame indices from a channel.
    work := make(chan int, nFrames)
    for i := range nFrames {
        work <- i
    }
    close(work)

    errs := make(chan error, nFrames)
    var wg sync.WaitGroup
    for range workers {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for i := range work {
                pos := (float64(i) + 0.5) * interval
                framePath := filepath.Join(tmpDir, fmt.Sprintf("frame_%03d.jpg", i+1))
                out, err := exec.Command("ffmpeg", "-y",
                    "-ss", fmt.Sprintf("%.3f", pos),
                    "-i", videoPath,
                    "-frames:v", "1",
                    "-vf", fmt.Sprintf("scale=%d:%d", thumbW, height),
                    "-q:v", "3",
                    "-v", "error",
                    framePath,
                ).CombinedOutput()
                if err != nil {
                    errs <- fmt.Errorf("frame %d at %.1fs: %w\n%s", i+1, pos, err, out)
                }
            }
        }()
    }

    wg.Wait()
    close(errs)

    for err := range errs {
        if err != nil {
            return err
        }
    }

    // Step 2: tile frames into spritesheet
    spritePath := filepath.Join(outDir, stem+".jpg")
    tileFilter := fmt.Sprintf("tile=%dx%d", cols, rows)
    framePattern := filepath.Join(tmpDir, "frame_%03d.jpg")
    out, err := exec.Command(
        "ffmpeg", "-y",
        "-i", framePattern,
        "-filter_complex", tileFilter,
        "-v", "error",
        spritePath,
    ).CombinedOutput()
    if err != nil {
        return fmt.Errorf("ffmpeg tile: %w\n%s", err, out)
    }

    // Step 3: generate VTT
    return writeSpritesheetVTT(filepath.Join(outDir, stem+".vtt"), stem, nFrames, cols, thumbW, height, interval)
}

func writeSpritesheetVTT(vttPath, stem string, nFrames, cols, thumbW, thumbH int, interval float64) error {
    var sb strings.Builder
    sb.WriteString("WEBVTT\n\n")
    for i := range nFrames {
        x := (i % cols) * thumbW
        y := (i / cols) * thumbH
        sb.WriteString(fmt.Sprintf(
            "%s --> %s\n%s.jpg#xywh=%d,%d,%d,%d\n\n",
            formatVTTTime(float64(i)*interval),
            formatVTTTime(float64(i+1)*interval),
            stem, x, y, thumbW, thumbH,
        ))
    }
    return os.WriteFile(vttPath, []byte(sb.String()), 0644)
}

// formatVTTTime converts seconds to "HH:MM:SS.mmm" for WebVTT.
func formatVTTTime(secs float64) string {
    h := int(secs) / 3600
    m := (int(secs) % 3600) / 60
    s := math.Mod(secs, 60)
    return fmt.Sprintf("%02d:%02d:%06.3f", h, m, s)
}

// probeVideoInfo returns (width, height, duration) for the first video stream.
func probeVideoInfo(videoPath string) (width, height int, duration float64, err error) {
    out, err := exec.Command(
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        videoPath,
    ).Output()
    if err != nil {
        return 0, 0, 0, fmt.Errorf("ffprobe: %w", err)
    }

    var probe struct {
        Streams []struct {
            CodecType string `json:"codec_type"`
            Width     int    `json:"width"`
            Height    int    `json:"height"`
        } `json:"streams"`
        Format struct {
            Duration string `json:"duration"`
        } `json:"format"`
    }
    if err := json.Unmarshal(out, &probe); err != nil {
        return 0, 0, 0, fmt.Errorf("ffprobe parse: %w", err)
    }

    if d, err2 := strconv.ParseFloat(probe.Format.Duration, 64); err2 == nil {
        duration = d
    }
    for _, s := range probe.Streams {
        if s.CodecType == "video" && s.Width > 0 && s.Height > 0 {
            width, height = s.Width, s.Height
            break
        }
    }
    if width == 0 || height == 0 {
        return 0, 0, 0, fmt.Errorf("no video stream found in %s", videoPath)
    }
    return width, height, duration, nil
}
