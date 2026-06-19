package mediagen

import (
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "strings"
)

// GenerateTeaser generates {stem}.mp4 in outDir from N short clips spread across the video.
// small=true: 640x360 scaled, 1.3s clips; false: full resolution, 1.65s clips.
func GenerateTeaser(videoPath, outDir, stem string, durationSecs float64, small bool) error {
    clipAmount := int((584.0/119 + (11.0/5355)*durationSecs) * 2)

    var nClips int
    var clipLen float64
    if small {
        nClips = clipAmount / 2
        clipLen = 1.3
    } else {
        nClips = clipAmount
        clipLen = 1.65
    }
    if nClips < 1 {
        nClips = 1
    }

    startSec := durationSecs * 0.05
    span := durationSecs*0.98 - startSec

    if err := os.MkdirAll(outDir, 0755); err != nil {
        return err
    }

    // Extract individual clips
    clipPaths := make([]string, 0, nClips)
    for i := 0; i < nClips; i++ {
        pos := startSec + float64(i)*span/float64(nClips)
        clipPath := filepath.Join(outDir, fmt.Sprintf("tmp_%s_%d.mp4", stem, i))

        args := []string{
            "-ss", fmt.Sprintf("%.3f", pos),
            "-i", videoPath,
            "-t", fmt.Sprintf("%.3f", clipLen),
            "-map", "0:v:0", "-an",
            "-c:v", "libx264",
        }
        if small {
            args = append(args, "-vf", "scale=640:360")
        }
        args = append(args, "-v", "error", "-y", clipPath)

        out, err := exec.Command("ffmpeg", args...).CombinedOutput()
        if err != nil {
            // Clean up any clips extracted so far
            for _, p := range clipPaths {
                os.Remove(p)
            }
            return fmt.Errorf("ffmpeg clip %d: %w\n%s", i, err, out)
        }
        clipPaths = append(clipPaths, clipPath)
    }

    defer func() {
        for _, p := range clipPaths {
            os.Remove(p)
        }
    }()

    return concatClips(clipPaths, filepath.Join(outDir, stem+".mp4"))
}

func concatClips(clipPaths []string, savePath string) error {
    args := []string{}
    var filterParts strings.Builder
    for i, p := range clipPaths {
        args = append(args, "-i", p)
        filterParts.WriteString(fmt.Sprintf("[%d:v]", i))
    }
    filterParts.WriteString(fmt.Sprintf("concat=n=%d:v=1 [v]", len(clipPaths)))

    args = append(args,
        "-filter_complex", filterParts.String(),
        "-map", "[v]",
        "-v", "error", "-stats",
        "-y", savePath,
    )

    out, err := exec.Command("ffmpeg", args...).CombinedOutput()
    if err != nil {
        return fmt.Errorf("ffmpeg concat: %w\n%s", err, out)
    }
    return nil
}
