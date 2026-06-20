package routes

import (
    "fmt"
    "net/http"
    "os"
    "slices"
    "sync"

    "github.com/labstack/echo/v4"

    "cpv_backend/internal/config"
    "cpv_backend/internal/db"
    "cpv_backend/internal/mediagen"
    "cpv_backend/internal/pyworker"
    "cpv_backend/internal/scanner"
)

// ─── Job broker ──────────────────────────────────────────────────────────────
// Fans log-lines from a running job out to all connected SSE clients.

type jobBroker struct {
    mu      sync.Mutex
    running bool
    log     []string
    subs    map[chan string]struct{}
}

var dashBroker = &jobBroker{subs: make(map[chan string]struct{})}

func (b *jobBroker) emit(line string) {
    b.mu.Lock()
    defer b.mu.Unlock()
    b.log = append(b.log, line)
    for ch := range b.subs {
        select {
        case ch <- line:
        default:
        }
    }
}

func (b *jobBroker) subscribe() ([]string, chan string) {
    b.mu.Lock()
    defer b.mu.Unlock()
    ch := make(chan string, 256)
    b.subs[ch] = struct{}{}
    snap := make([]string, len(b.log))
    copy(snap, b.log)
    return snap, ch
}

func (b *jobBroker) unsubscribe(ch chan string) {
    b.mu.Lock()
    defer b.mu.Unlock()
    delete(b.subs, ch)
}

// start runs fn in a goroutine; returns false if a job is already running.
func (b *jobBroker) start(fn func(emit func(string))) bool {
    b.mu.Lock()
    if b.running {
        b.mu.Unlock()
        return false
    }
    b.running = true
    b.log = nil
    b.mu.Unlock()

    go func() {
        fn(b.emit)
        b.emit("\x00DONE")
        b.mu.Lock()
        b.running = false
        b.mu.Unlock()
    }()
    return true
}

// ─── Route registration ──────────────────────────────────────────────────────

func IncludeDashboardRoutes(e *echo.Group, store *config.ConfigStore) {
    e.GET("/stats",           func(c echo.Context) error { return ECHO_dashboard_stats(c, store.Current().DBPath) })
    e.GET("/media-status",    func(c echo.Context) error { cfg := store.Current(); return ECHO_dashboard_media_status(c, cfg.DBPath, cfg.PreviewMediaDir) })
    e.POST("/run-scan",       func(c echo.Context) error { return ECHO_dashboard_run_scan(c, store.Current()) })
    e.POST("/generate-media", func(c echo.Context) error { return ECHO_dashboard_generate_media(c, store.Current()) })
    e.POST("/rebuild-tfidf",  func(c echo.Context) error { return ECHO_dashboard_rebuild_tfidf(c, store.Current()) })
    e.GET("/job-stream",      ECHO_dashboard_job_stream)
}

// ─── Stats ───────────────────────────────────────────────────────────────────

type DashboardStats struct {
    TotalVideos    int              `json:"total_videos"`
    LinkedVideos   int              `json:"linked_videos"`
    UnlinkedVideos int              `json:"unlinked_videos"`
    Collections    []CollectionStat `json:"collections"`
}

type CollectionStat struct {
    Name  string `json:"name"`
    Count int    `json:"count"`
}

func ECHO_dashboard_stats(c echo.Context, dbPath string) error {
    mp, err := db.GetCachedVideos(dbPath, 15, 3)
    if err != nil {
        return handleServerError(c, 500, "Unable to read database", err)
    }

    linked, unlinked := 0, 0
    colls := map[string]int{}
    for _, vd := range mp {
        if vd.IsLinked {
            linked++
        } else {
            unlinked++
        }
        if vd.Collection != "" {
            colls[vd.Collection]++
        }
    }

    collections := make([]CollectionStat, 0, len(colls))
    for name, count := range colls {
        collections = append(collections, CollectionStat{Name: name, Count: count})
    }
    slices.SortFunc(collections, func(a, b CollectionStat) int {
        return b.Count - a.Count
    })

    return c.JSON(200, DashboardStats{
        TotalVideos:    len(mp),
        LinkedVideos:   linked,
        UnlinkedVideos: unlinked,
        Collections:    collections,
    })
}

// ─── Media status ────────────────────────────────────────────────────────────

type MediaTypeStatus struct {
    With    int     `json:"with"`
    Without int     `json:"without"`
    Total   int     `json:"total"`
    Pct     float64 `json:"pct"`
}

type MediaStatusResponse struct {
    TeaserThumbs  MediaTypeStatus `json:"teaser_thumbs"`
    SeekThumbs    MediaTypeStatus `json:"seek_thumbs"`
    Teasers       MediaTypeStatus `json:"teasers"`
    PreviewThumbs MediaTypeStatus `json:"preview_thumbs"`
}

func ECHO_dashboard_media_status(c echo.Context, dbPath, previewMediaDir string) error {
    mp, err := db.GetCachedVideos(dbPath, 15, 3)
    if err != nil {
        return handleServerError(c, 500, "Unable to read database", err)
    }

    var tt, st, te, pt MediaTypeStatus
    exists := func(path string) bool { _, e := os.Stat(path); return e == nil }

    for _, vd := range mp {
        if !vd.IsLinked {
            continue
        }
        dir := getVideoMediaDir(previewMediaDir, vd.Hash)

        if exists(dir + "/teaser_thumbs_small.jpg") { tt.With++ } else { tt.Without++ }
        if exists(dir+"/seekthumbs.jpg") && exists(dir+"/seekthumbs.vtt") { st.With++ } else { st.Without++ }
        if exists(dir + "/teaser_small.mp4") { te.With++ } else { te.Without++ }
        entries, _ := os.ReadDir(dir + "/previewthumbs")
        if len(entries) >= 10 { pt.With++ } else { pt.Without++ }
    }

    finalize := func(s *MediaTypeStatus) {
        s.Total = s.With + s.Without
        if s.Total > 0 {
            s.Pct = float64(s.With) / float64(s.Total) * 100
        }
    }
    finalize(&tt); finalize(&st); finalize(&te); finalize(&pt)

    return c.JSON(200, MediaStatusResponse{tt, st, te, pt})
}

// ─── Job endpoints (stubs; real logic added in Stage 2b/2c) ──────────────────

func ECHO_dashboard_run_scan(c echo.Context, cfg config.Config) error {
    var opts scanner.ScanOptions
    if err := c.Bind(&opts); err != nil {
        return c.JSON(400, map[string]string{"error": "invalid request body"})
    }
    started := dashBroker.start(func(emit func(string)) {
        if err := scanner.ScanLibraries(cfg, opts, emit); err != nil {
            emit(fmt.Sprintf("[ERROR] Scan failed: %v", err))
        }
    })
    if !started {
        return c.JSON(409, map[string]string{"error": "A job is already running"})
    }
    return c.JSON(202, map[string]string{"status": "started"})
}

func ECHO_dashboard_generate_media(c echo.Context, cfg config.Config) error {
    var opts mediagen.GenerateMediaOptions
    if err := c.Bind(&opts); err != nil {
        return c.JSON(400, map[string]string{"error": "invalid request body"})
    }
    started := dashBroker.start(func(emit func(string)) {
        if err := mediagen.BatchGenerate(cfg, opts, emit); err != nil {
            emit(fmt.Sprintf("[ERROR] Media generation failed: %v", err))
        }
    })
    if !started {
        return c.JSON(409, map[string]string{"error": "A job is already running"})
    }
    return c.JSON(202, map[string]string{"status": "started"})
}

func ECHO_dashboard_rebuild_tfidf(c echo.Context, cfg config.Config) error {
    started := dashBroker.start(func(emit func(string)) {
        emit("[TFIDF] Building TF-IDF model…")
        tt, err := pyworker.Exec(
            "-m", "cmd.generateTFIDF",
            "--db-path", cfg.DBPath,
            "--model-dir", cfg.AppDataDir,
        )
        if err != nil {
            emit(fmt.Sprintf("[TFIDF] Failed: %v", err))
            return
        }
        emit(fmt.Sprintf("[TFIDF] Done in %.1fs.", tt))
    })
    if !started {
        return c.JSON(409, map[string]string{"error": "A job is already running"})
    }
    return c.JSON(202, map[string]string{"status": "started"})
}

// ─── SSE stream ──────────────────────────────────────────────────────────────

func ECHO_dashboard_job_stream(c echo.Context) error {
    w := c.Response()
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    w.WriteHeader(http.StatusOK)

    snap, ch := dashBroker.subscribe()
    defer dashBroker.unsubscribe(ch)

    sendLine := func(line string) {
        fmt.Fprintf(w, "data: %s\n\n", line)
        w.Flush()
    }

    for _, line := range snap {
        if line == "\x00DONE" {
            fmt.Fprintf(w, "event: done\ndata: \n\n")
            w.Flush()
            return nil
        }
        sendLine(line)
    }

    ctx := c.Request().Context()
    for {
        select {
        case <-ctx.Done():
            return nil
        case line, ok := <-ch:
            if !ok || line == "\x00DONE" {
                fmt.Fprintf(w, "event: done\ndata: \n\n")
                w.Flush()
                return nil
            }
            sendLine(line)
        }
    }
}
