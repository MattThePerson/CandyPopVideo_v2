package routes

import (
    "cpv_backend/internal/db"
    "cpv_backend/internal/mediagen"
    "cpv_backend/internal/pyworker"
    "cpv_backend/internal/schemas"
    "fmt"
    "net/http"
    "os"
    "os/exec"
    "path/filepath"
    "strconv"
    "strings"
    "log"

    "github.com/labstack/echo/v4"
)

// onDemandSem limits concurrent on-demand ffmpeg generation (hover events, teaser-large).
// Without this, hovering 24 cards simultaneously would spawn 24*n concurrent ffmpeg processes.
var onDemandSem = make(chan struct{}, 1)

// previewThumbsSem limits concurrent Python preview-thumb generation (slow ML subprocess).
// Separate from onDemandSem so a thumbs job and a teaser job don't block each other.
var previewThumbsSem = make(chan struct{}, 1)

func IncludeMediaRoutes(e *echo.Group, db_path string, preview_media_dir string, subtitle_folders []string) {

    e.GET("/get/video/:video_hash", func(c echo.Context) error { return ECHO_get_video(c, db_path) })
    e.GET("/get/poster/:video_hash", func(c echo.Context) error { return ECHO_get_poster(c, db_path, preview_media_dir) })
    e.GET("/preview/:video_hash/*",  func(c echo.Context) error { return ECHO_get_preview_media(c, db_path, preview_media_dir) })
    e.HEAD("/preview/:video_hash/*", func(c echo.Context) error { return ECHO_get_preview_media(c, db_path, preview_media_dir) })
    e.GET("/ensure/teaser-small/:video_hash",        func(c echo.Context) error { return ECHO_ensure_teaser_small(c, db_path, preview_media_dir) })
    e.GET("/ensure/teaser-large/:video_hash",        func(c echo.Context) error { return ECHO_ensure_teaser_large(c, db_path, preview_media_dir) })
    e.GET("/ensure/teaser-thumbs-small/:video_hash", func(c echo.Context) error { return ECHO_ensure_teaser_thumbs_small(c, db_path, preview_media_dir) })
    e.GET("/ensure/seek-thumbnails/:video_hash",     func(c echo.Context) error { return ECHO_ensure_seek_thumbs(c, db_path, preview_media_dir) })
    e.GET("/ensure/preview-thumbs/:video_hash",      func(c echo.Context) error { return ECHO_ensure_preview_thumbs(c, db_path, preview_media_dir) })
    e.GET("/get/subtitles/:video_hash", func(c echo.Context) error { return ECHO_get_subs(c, db_path, preview_media_dir, subtitle_folders) })
    e.GET("/get/preview-thumbs/:video_hash", func(c echo.Context) error { return ECHO_get_preview_thumbs(c, preview_media_dir) })

}

// ECHO_get_video ...
func ECHO_get_video(c echo.Context, db_path string) error {
    video_hash := c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }
    if strings.HasSuffix(strings.ToLower(vd.Path), ".mkv") {
        return get_mkv_file_response(c, vd.Path)
    }
    return c.File(vd.Path)
}

func get_mkv_file_response(c echo.Context, video_path string) error {
    c.Response().Header().Set(echo.HeaderContentType, "video/mp4")
    c.Response().WriteHeader(http.StatusOK)

    cmd := exec.Command(
        "ffmpeg",
        "-i", video_path,
        "-c", "copy",
        "-movflags", "frag_keyframe+empty_moov",
        "-f", "mp4",
        "pipe:1",
    )

    cmd.Stdout = c.Response().Writer
    cmd.Stderr = os.Stderr
    err := cmd.Run()

    if err != nil {
        return err
    }
    return nil
}

// ECHO_get_poster ...
func ECHO_get_poster(c echo.Context, db_path string, preview_media_dir string) error {
    var video_hash = c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)

    // check for preview thumbs
    // HEREEEEE
    large_thumbs := c.QueryParam("large") == "true"
    preview_thumb, err := getPreviewThumbnail(vid_media_dir, large_thumbs)
    if err == nil {
        // fmt.Println("FOUND PREVIEW THUMB: "+preview_thumb)
        return c.File(preview_thumb)
    }

    // check for poster
    var poster_pth = vid_media_dir + "/poster.png"
    if _, err := os.Stat(poster_pth); err == nil {
        return c.File(poster_pth)
    }

    // get video data
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    // [subprocess] video poster
    fmt.Println("[subprocess] creating `Simple Poster` for: " + video_hash + " ...")
    os.MkdirAll(vid_media_dir, 0755)
    cmd := exec.Command(
        "ffmpeg",
        "-ss", strconv.Itoa(int(vd.DurationSeconds*0.2)),
        "-i", vd.Path,
        "-frames:v", "1",
        poster_pth,
        "-loglevel", "quiet",
    )
    if _, err := cmd.CombinedOutput(); err != nil {
        return handleServerError(c, 500, "Unable to generate simple poster", err)
    }

    // check media exists
    if _, err := os.Stat(poster_pth); err == nil {
        return c.File(poster_pth)
    }

    return c.String(500, "Unable to create `Simple Poster` for hash: "+video_hash)
}

// ECHO_get_preview_media
func ECHO_get_preview_media(c echo.Context, db_path string, preview_media_dir string) error {
    video_hash := c.Param("video_hash")
    filename := c.Param("*") // eg. seekthumbs.jpg
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    return c.File(filepath.Join(getVideoMediaDir(preview_media_dir, video_hash), filename))
}

// ECHO_ensure_teaser_small ...
func ECHO_ensure_teaser_small(c echo.Context, db_path string, preview_media_dir string) error {
    var video_hash = c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
    var media_stem = "teaser_small.mp4"
    var media_path = vid_media_dir + "/" + media_stem
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }

    // get video data
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    fmt.Printf("[MEDIA] Generating 'Video Teaser (small)' for: %s ...\n", video_hash)
    onDemandSem <- struct{}{}
    err = mediagen.GenerateTeaser(vd.Path, vid_media_dir, "teaser_small", vd.DurationSeconds, true)
    <-onDemandSem
    if err != nil {
        return handleServerError(c, 500, "Unable to generate teaser small", err)
    }

    // check media exists
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }
    return c.String(500, "Unable to create `Video Teaser (small)` for hash: "+video_hash)
}

// ECHO_ensure_teaser_large generates teaser_large.mp4 at full resolution if missing.
func ECHO_ensure_teaser_large(c echo.Context, db_path string, preview_media_dir string) error {
    var video_hash = c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
    var media_path = vid_media_dir + "/teaser_large.mp4"
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }

    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    fmt.Printf("[MEDIA] Generating 'Video Teaser (large)' for: %s ...\n", video_hash)
    onDemandSem <- struct{}{}
    err = mediagen.GenerateTeaser(vd.Path, vid_media_dir, "teaser_large", vd.DurationSeconds, false)
    <-onDemandSem
    if err != nil {
        return handleServerError(c, 500, "Unable to generate teaser large", err)
    }

    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "generated")
    }
    return c.String(500, "Unable to create `Video Teaser (large)` for hash: "+video_hash)
}

// ECHO_ensure_preview_thumbs runs the ML preview-thumb Python worker if thumbs are missing.
func ECHO_ensure_preview_thumbs(c echo.Context, db_path string, preview_media_dir string) error {
    var video_hash = c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))

    thumbsDir := getVideoMediaDir(preview_media_dir, video_hash) + "/previewthumbs"
    if entries, err := os.ReadDir(thumbsDir); err == nil && len(entries) >= 10 {
        return c.String(200, "preview thumbs already exist")
    }

    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    fmt.Printf("[MEDIA] Generating 'Preview Thumbs' for: %s ...\n", video_hash)
    previewThumbsSem <- struct{}{}
    _, err = pyworker.Exec(
        "-m", "cmd.generatePreviewThumbs",
        "--video-path", vd.Path,
        "--hash", video_hash,
        "--media-dir", preview_media_dir+"/preview",
    )
    <-previewThumbsSem
    if err != nil {
        return handleServerError(c, 500, "Unable to generate preview thumbs", err)
    }

    return c.String(200, "generated")
}

// ECHO_ensure_teaser_thumbs_small ...
func ECHO_ensure_teaser_thumbs_small(c echo.Context, db_path string, preview_media_dir string) error {
    var video_hash = c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
    var media_path = vid_media_dir + "/teaser_thumbs_small.jpg"
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }

    // get video data
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    fmt.Printf("[MEDIA] Generating 'Teaser Thumbs (small)' for: %s ...\n", video_hash)
    onDemandSem <- struct{}{}
    err = mediagen.GenerateSpritesheet(vd.Path, vid_media_dir, "teaser_thumbs_small", 16, 300, 6)
    <-onDemandSem
    if err != nil {
        return handleServerError(c, 500, "Unable to generate teaser thumbs", err)
    }

    // check media exists
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }
    return c.String(500, "Unable to create `Teaser Thumbs (small)` for hash: "+video_hash)
}

// ECHO_ensure_seek_thumbs ...
func ECHO_ensure_seek_thumbs(c echo.Context, db_path string, preview_media_dir string) error {
    var video_hash = c.Param("video_hash")
    video_hash = resolveDevHash(video_hash, c.QueryParam("dev"))
    var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
    var media_path = vid_media_dir + "/seekthumbs.jpg"
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }

    // get video data
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    fmt.Printf("[MEDIA] Generating 'Seek Thumbs' for: %s ...\n", video_hash)
    onDemandSem <- struct{}{}
    err = mediagen.GenerateSpritesheet(vd.Path, vid_media_dir, "seekthumbs", 400, 300, 1)
    <-onDemandSem
    if err != nil {
        return handleServerError(c, 500, "Unable to generate seek thumbs", err)
    }

    // check media exists
    if _, err := os.Stat(media_path); err == nil {
        return c.String(200, "media exists")
    }
    return c.String(500, "Unable to create `Seek Thumbs` for hash: "+video_hash)
}

// ECHO_get_preview_thumbs returns the filenames of large (1080p) ML preview thumbnails for a video.
// Returns an empty array if the previewthumbs directory doesn't exist or has no 1080 images.
// Filenames can be resolved to URLs via /media/preview/:hash/previewthumbs/<filename>.
func ECHO_get_preview_thumbs(c echo.Context, preview_media_dir string) error {
    video_hash := c.Param("video_hash")
    thumbs_dir := getVideoMediaDir(preview_media_dir, video_hash) + "/previewthumbs"

    filenames := []string{}
    entries, err := os.ReadDir(thumbs_dir)
    if err == nil {
        for _, e := range entries {
            if strings.Contains(e.Name(), "1080") {
                filenames = append(filenames, e.Name())
            }
        }
    }

    return c.JSON(200, filenames)
}

// ECHO_get_subs ...
func ECHO_get_subs(c echo.Context, db_path string, preview_media_dir string, subtitle_folders []string) error {
    video_hash := c.Param("video_hash")
    check := c.QueryParam("check") == "true"
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }

    serve := func(path string) error {
        if check {
            return c.String(200, "All good bro")
        }
        return c.File(path)
    }

    // get id for srt file: "<id>.srt"
    id_options := []string{
        vd.SourceID,
        vd.DVDCode,
        strings.TrimSuffix(vd.Filename, filepath.Ext(vd.Path)),
    }
    id := ""
    for _, s := range id_options {
        if s != "" {
            id = s
            break
        }
    }

    // check folders for external srt
    parent_dir := filepath.Dir(vd.Path)
    check_folders := []string{
        parent_dir,
        filepath.Join(parent_dir, ".subtitles"),
    }
    check_folders = append(check_folders, subtitle_folders...)
    for _, f := range check_folders {
        pth := filepath.Join(f, id+".srt")
        if _, err := os.Stat(pth); err == nil {
            fmt.Println("FOUND IT")
            return serve(pth)
        }
    }

    // check cached extracted subtitle
    subtitles_dir := filepath.Join(preview_media_dir, "subtitles")
    cached_path := filepath.Join(subtitles_dir, video_hash+".srt")
    if _, err := os.Stat(cached_path); err == nil {
        return serve(cached_path)
    }

    // extract embedded subtitle stream (mp4 only)
    if filepath.Ext(vd.Path) != ".mp4" {
        return c.NoContent(404)
    }
    if err := mediagen.ExtractSubtitleStream(vd.Path, cached_path); err != nil {
        log.Printf("[SUBS] no subtitle stream in %s: %v", vd.Path, err)
        return c.NoContent(404)
    }
    return serve(cached_path)
}
