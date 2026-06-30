package mediagen

import (
    "encoding/json"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
)

var textSubtitleCodecs = map[string]bool{
    "srt":      true,
    "subrip":   true,
    "mov_text": true,
    "ass":      true,
    "ssa":      true,
    "webvtt":   true,
}

type ffprobeStream struct {
    Index     int    `json:"index"`
    CodecName string `json:"codec_name"`
}

type ffprobeOutput struct {
    Streams []ffprobeStream `json:"streams"`
}

// ExtractSubtitleStream finds the first text-based subtitle stream in videoPath
// and extracts it as SRT to outputPath. Returns an error if no suitable stream
// is found or if extraction fails.
func ExtractSubtitleStream(videoPath, outputPath string) error {
    streamIndex, err := findTextSubtitleStream(videoPath)
    if err != nil {
        return err
    }

    if err := os.MkdirAll(filepath.Dir(outputPath), 0755); err != nil {
        return err
    }

    args := []string{
        "-i", videoPath,
        "-map", fmt.Sprintf("0:%d", streamIndex),
        "-c:s", "srt",
        "-v", "error",
        "-y", outputPath,
    }
    out, err := exec.Command("ffmpeg", args...).CombinedOutput()
    if err != nil {
        return fmt.Errorf("ffmpeg subtitle extract: %w\n%s", err, out)
    }
    return nil
}

func findTextSubtitleStream(videoPath string) (int, error) {
    args := []string{
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index,codec_name",
        "-of", "json",
        videoPath,
    }
    out, err := exec.Command("ffprobe", args...).Output()
    if err != nil {
        return 0, fmt.Errorf("ffprobe: %w", err)
    }

    var result ffprobeOutput
    if err := json.Unmarshal(out, &result); err != nil {
        return 0, fmt.Errorf("ffprobe parse: %w", err)
    }

    for _, s := range result.Streams {
        if textSubtitleCodecs[s.CodecName] {
            return s.Index, nil
        }
    }
    return 0, fmt.Errorf("no text-based subtitle stream found")
}
