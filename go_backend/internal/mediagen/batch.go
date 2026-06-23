package mediagen

import (
    "fmt"
    "os"
    "path/filepath"
    "strings"
    "time"

    "cpv_backend/internal/config"
    "cpv_backend/internal/db"
    "cpv_backend/internal/pyworker"
    "cpv_backend/internal/schemas"
)

type GenerateMediaOptions struct {
    MediaType  string `json:"media_type"`  // "all" | "teasers" | "teaser_thumbs" | "seek_thumbs"
    Redo       bool   `json:"redo"`
    Collection string `json:"collection"`  // "" = all collections
    PathFilter string `json:"path_filter"` // case-insensitive substring on vd.Path
    DaysFilter int    `json:"days_filter"` // 0 = all; N = added within last N days
}

// BatchGenerate runs media generation for all matching linked videos.
func BatchGenerate(cfg config.Config, opts GenerateMediaOptions, emit func(string)) error {
    all, err := db.ReadLinkedVideosMap(cfg.DBPath)
    if err != nil {
        return fmt.Errorf("reading DB: %w", err)
    }

    cutoff := time.Time{}
    if opts.DaysFilter > 0 {
        cutoff = time.Now().AddDate(0, 0, -opts.DaysFilter)
    }

    var videos []schemas.VideoData
    for _, vd := range all {
        if opts.Collection != "" && vd.Collection != opts.Collection {
            continue
        }
        if opts.PathFilter != "" && !strings.Contains(strings.ToLower(vd.Path), strings.ToLower(opts.PathFilter)) {
            continue
        }
        if !cutoff.IsZero() {
            t, err := time.Parse("2006-01-02 15:04", vd.DateAdded)
            if err == nil && t.Before(cutoff) {
                continue
            }
        }
        videos = append(videos, vd)
    }

    emit(fmt.Sprintf("[MEDIA] %d videos to process", len(videos)))

    doTeasers := opts.MediaType == "all" || opts.MediaType == "teasers"
    doTeaserThumbs := opts.MediaType == "all" || opts.MediaType == "teaser_thumbs"
    doSeekThumbs := opts.MediaType == "all" || opts.MediaType == "seek_thumbs"
    doPreviewThumbs := opts.MediaType == "preview_thumbs" // not included in "all" — slow ML extraction

    generated, errCount := 0, 0

    for i, vd := range videos {
        vidDir := fmt.Sprintf("%s/preview/0x%s", cfg.PreviewMediaDir, vd.Hash)

        if doTeasers {
            p := vidDir + "/teaser_small.mp4"
            if opts.Redo || !fileExists(p) {
                if err := GenerateTeaser(vd.Path, vidDir, "teaser_small", vd.DurationSeconds, true); err != nil {
                    emit(fmt.Sprintf("[WARN] teaser %s: %v", vd.Hash, err))
                    errCount++
                } else {
                    generated++
                }
            }
        }

        if doTeaserThumbs {
            p := vidDir + "/teaser_thumbs_small.jpg"
            if opts.Redo || !fileExists(p) {
                if err := GenerateSpritesheet(vd.Path, vidDir, "teaser_thumbs_small", 16, 300, 3); err != nil {
                    emit(fmt.Sprintf("[WARN] teaser thumbs %s: %v", vd.Hash, err))
                    errCount++
                } else {
                    generated++
                }
            }
        }

        if doSeekThumbs {
            p := vidDir + "/seekthumbs.jpg"
            if opts.Redo || !fileExists(p) {
                if err := GenerateSpritesheet(vd.Path, vidDir, "seekthumbs", 400, 300, 6); err != nil {
                    emit(fmt.Sprintf("[WARN] seek thumbs %s: %v", vd.Hash, err))
                    errCount++
                } else {
                    generated++
                }
            }
        }

        if doPreviewThumbs {
            thumbsDir := filepath.Join(vidDir, "previewthumbs")
            entries, _ := os.ReadDir(thumbsDir)
            if opts.Redo || len(entries) < 10 {
                if _, err := pyworker.Exec(
                    "-m", "cmd.generatePreviewThumbs",
                    "--video-path", vd.Path,
                    "--hash", vd.Hash,
                    "--media-dir", cfg.PreviewMediaDir+"/preview",
                ); err != nil {
                    emit(fmt.Sprintf("[WARN] preview thumbs %s: %v", vd.Hash, err))
                    errCount++
                } else {
                    generated++
                }
            }
        }

        if (i+1)%10 == 0 || i+1 == len(videos) {
            emit(fmt.Sprintf("[MEDIA] Processed %d / %d", i+1, len(videos)))
        }
    }

    emit(fmt.Sprintf("[MEDIA] Done. %d generated, %d errors.", generated, errCount))
    return nil
}

func fileExists(path string) bool {
    _, err := os.Stat(path)
    return err == nil
}
