package mediagen

import (
    "bytes"
    "encoding/json"
    "fmt"
    "image"
    "image/draw"
    "image/jpeg"
    "math"
    "os"
    "os/exec"
    "path/filepath"
    "strconv"
    "strings"
    "sync"
    "syscall"
)

type frameResult struct {
    index int
    data  []byte
    err   error
}

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

    canvas := image.NewRGBA(image.Rect(0, 0, thumbW*cols, height*rows))

    // Step 1: extract N frames via ffmpeg stdout pipe.
    // -ss before -i is fast-seek (nearest keyframe, no full decode).
    // -f mjpeg pipe:1 streams each frame as JPEG bytes to stdout — no disk I/O per frame.
    work := make(chan int, nFrames)
    for i := range nFrames {
        work <- i
    }
    close(work)

    results := make(chan frameResult, nFrames)
    var wg sync.WaitGroup
    for range workers {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for i := range work {
                pos := (float64(i) + 0.5) * interval
                cmd := exec.Command("ffmpeg",
                    "-ss", fmt.Sprintf("%.3f", pos),
                    "-i", videoPath,
                    "-frames:v", "1",
                    "-vf", fmt.Sprintf("scale=%d:%d", thumbW, height),
                    "-q:v", "3",
                    "-v", "error",
                    "-f", "mjpeg", "pipe:1",
                )
                cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
                var stderr bytes.Buffer
                cmd.Stderr = &stderr
                data, err := cmd.Output()
                if err != nil {
                    results <- frameResult{index: i, err: fmt.Errorf("frame %d at %.1fs: %w\n%s", i+1, pos, err, stderr.String())}
                } else {
                    results <- frameResult{index: i, data: data}
                }
            }
        }()
    }

    wg.Wait()
    close(results)

    // Step 2: decode each frame and draw onto the canvas.
    for r := range results {
        if r.err != nil {
            return r.err
        }
        img, err := jpeg.Decode(bytes.NewReader(r.data))
        if err != nil {
            return fmt.Errorf("decode frame %d: %w", r.index+1, err)
        }
        col := r.index % cols
        row := r.index / cols
        dstRect := image.Rect(col*thumbW, row*height, (col+1)*thumbW, (row+1)*height)
        draw.Draw(canvas, dstRect, img, image.Point{}, draw.Src)
    }

    // Step 3: encode and write the spritesheet.
    spritePath := filepath.Join(outDir, stem+".jpg")
    f, err := os.Create(spritePath)
    if err != nil {
        return fmt.Errorf("create spritesheet: %w", err)
    }
    defer f.Close()
    if err := jpeg.Encode(f, canvas, &jpeg.Options{Quality: 88}); err != nil {
        return fmt.Errorf("encode spritesheet: %w", err)
    }

    // Step 4: generate VTT
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
    cmd := exec.Command(
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        videoPath,
    )
    cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
    out, err := cmd.Output()
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
