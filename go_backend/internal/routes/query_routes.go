package routes

import (
    "encoding/json"
    "fmt"
    "slices"
    "strings"
    "time"

    "github.com/labstack/echo/v4"

    "cpv_backend/internal/config"
    "cpv_backend/internal/db"
    "cpv_backend/internal/pyworker"
    "cpv_backend/internal/query"
    "cpv_backend/internal/schemas"
)

// StrictBind binds received JSON to a struct, rejecting unknown fields.
func StrictBind(c echo.Context, s any) error {
    decoder := json.NewDecoder(c.Request().Body)
    decoder.DisallowUnknownFields()
    if err := decoder.Decode(&s); err != nil {
        return c.String(400, "Invalid JSON: "+err.Error())
    }
    return nil
}

func IncludeQueryRoutes(e *echo.Group, db_path string, tfidfMatrixPath string, actorProfilesPath string, studioProfilesPath string, stateStore *config.AppStateStore) {
    e.POST("/search-videos",                    func(c echo.Context) error { return ECHO_search_videos(c, db_path, stateStore) })
    e.POST("/get/catalogue",                    func(c echo.Context) error { return ECHO_get_catalogue(c, db_path, stateStore) })
    e.POST("/get/item-counts",                  func(c echo.Context) error { return ECHO_get_item_counts(c, db_path, stateStore) })
    e.GET("/get/similar-videos/:video_hash",    func(c echo.Context) error { return ECHO_get_similar_videos(c, db_path, tfidfMatrixPath, stateStore) })
    e.GET("/get/suggested-videos/:video_hash",  func(c echo.Context) error { return ECHO_get_suggested_videos(c, db_path, tfidfMatrixPath, stateStore) })
    e.GET("/get/similar-actors/:name",          func(c echo.Context) error { return ECHO_get_similar_actors(c, actorProfilesPath) })
    e.GET("/get/similar-studios/:name",         func(c echo.Context) error { return ECHO_get_similar_studios(c, studioProfilesPath) })
}


// ECHO_search_videos
func ECHO_search_videos(c echo.Context, db_path string, stateStore *config.AppStateStore) error {
    var q schemas.SearchQuery
    if err := StrictBind(c, &q); err != nil {
        return c.String(400, "Invalid JSON: "+err.Error())
    }

    vids, err := getFilteredVideos(db_path, stateStore)
    if err != nil {
        return handleServerError(c, 500, "Unable to read videos table", err)
    }

    i, err := db.GetCachedInteractions(db_path, 15, 3)
    if err != nil {
        return handleServerError(c, 500, "Unable to read interactions table", err)
    }

    results, err := query.FilterAndSortVideos(vids, q, i)
    if err != nil {
        return handleServerError(c, 500, "Unable to filter and sort videos", err)
    }

    // TODO: sort by TF-IDF score when q.SearchString != ""

    return c.JSON(200, results)
}


// ECHO_get_catalogue
func ECHO_get_catalogue(c echo.Context, db_path string, stateStore *config.AppStateStore) error {
    var q schemas.CatalogueQuery
    if err := StrictBind(c, &q); err != nil {
        return c.String(400, "Invalid JSON: "+err.Error())
    }

    vids, err := getFilteredVideos(db_path, stateStore)
    if err != nil {
        return handleServerError(c, 500, "Unable to read videos table", err)
    }

    cat, err := query.GetCatalogue(vids, q)
    if err != nil {
        return handleServerError(c, 500, "Unable to get catalogue", err)
    }
    return c.JSON(200, cat)
}


// ECHO_get_similar_videos
func ECHO_get_similar_videos(c echo.Context, db_path string, tfidfMatrixPath string, stateStore *config.AppStateStore) error {
    video_hash := c.Param("video_hash")

    type SubprocessResponse struct {
        HashesList []string
        SimsList   []float64
        Report     string
    }

    fmt.Printf("[EXEC] Fetching similar videos for `%s` ...\n", video_hash)
    start := time.Now()
    response, err := pyworker.ExecOutput[SubprocessResponse](
        "-m", "cmd.getSimilarVideos",
        "--target", video_hash,
        "--model-path", tfidfMatrixPath,
    )
    if err != nil {
        return handleServerError(c, 500, "Python subprocess failed", err)
    }
    tt := time.Since(start).Seconds()
    fmt.Printf("[EXEC] Done. Took %.2f sec\n", tt)
    fmt.Printf("[EXEC] REPORT: %s\n", response.Report)

    // Build a fast lookup from the filtered pool
    vids, err := getFilteredVideos(db_path, stateStore)
    if err != nil {
        return handleServerError(c, 500, "Unable to read videos table", err)
    }
    filteredMap := make(map[string]schemas.VideoData, len(vids))
    for _, vd := range vids {
        filteredMap[vd.Hash] = vd
    }

    // Walk TF-IDF results in ranked order, keeping only filtered videos
    videos := []schemas.VideoData{}
    sims := map[string]float64{}
    for idx, hsh := range response.HashesList {
        vd, ok := filteredMap[hsh]
        if !ok {
            continue
        }
        videos = append(videos, vd)
        sims[hsh] = response.SimsList[idx]
    }

    type Reply struct {
        TimeTaken float64
        Videos    []schemas.VideoData
        SimScores map[string]float64
    }
    return c.JSON(200, Reply{TimeTaken: tt, Videos: videos, SimScores: sims})
}

// ECHO_get_similar_actors
func ECHO_get_similar_actors(c echo.Context, actorProfilesPath string) error {
    name := c.Param("name")

    type SubprocessResponse struct {
        NamesList []string
        SimsList  []float64
        Report    string
    }

    fmt.Printf("[EXEC] Fetching similar actors for `%s` ...\n", name)
    start := time.Now()
    response, err := pyworker.ExecOutput[SubprocessResponse](
        "-m", "cmd.getSimilarActors",
        "--target", name,
        "--model-path", actorProfilesPath,
    )
    if err != nil {
        return handleServerError(c, 500, "Python subprocess failed", err)
    }
    tt := time.Since(start).Seconds()
    fmt.Printf("[EXEC] Done. Took %.2f sec\n", tt)
    fmt.Printf("[EXEC] REPORT: %s\n", response.Report)

    type Reply struct {
        TimeTaken float64
        NamesList []string
        SimScores map[string]float64
    }
    simScores := make(map[string]float64, len(response.NamesList))
    for idx, n := range response.NamesList {
        simScores[n] = response.SimsList[idx]
    }
    return c.JSON(200, Reply{TimeTaken: tt, NamesList: response.NamesList, SimScores: simScores})
}

// ECHO_get_similar_studios
func ECHO_get_similar_studios(c echo.Context, studioProfilesPath string) error {
    name := c.Param("name")

    type SubprocessResponse struct {
        NamesList []string
        SimsList  []float64
        Report    string
    }

    fmt.Printf("[EXEC] Fetching similar studios for `%s` ...\n", name)
    start := time.Now()
    response, err := pyworker.ExecOutput[SubprocessResponse](
        "-m", "cmd.getSimilarStudios",
        "--target", name,
        "--model-path", studioProfilesPath,
    )
    if err != nil {
        return handleServerError(c, 500, "Python subprocess failed", err)
    }
    tt := time.Since(start).Seconds()
    fmt.Printf("[EXEC] Done. Took %.2f sec\n", tt)
    fmt.Printf("[EXEC] REPORT: %s\n", response.Report)

    type Reply struct {
        TimeTaken float64
        NamesList []string
        SimScores map[string]float64
    }
    simScores := make(map[string]float64, len(response.NamesList))
    for idx, n := range response.NamesList {
        simScores[n] = response.SimsList[idx]
    }
    return c.JSON(200, Reply{TimeTaken: tt, NamesList: response.NamesList, SimScores: simScores})
}

// ECHO_get_suggested_videos — TF-IDF similar videos re-ranked by user popularity + platform stats,
// with recently-viewed videos filtered out. Query param ignore_last (Go duration, default "24h").
func ECHO_get_suggested_videos(c echo.Context, db_path string, tfidfMatrixPath string, stateStore *config.AppStateStore) error {
    videoHash := c.Param("video_hash")

    ignoreLast := 24 * time.Hour
    if raw := c.QueryParam("ignore_last"); raw != "" {
        if d, err := time.ParseDuration(raw); err == nil {
            ignoreLast = d
        }
    }
    cutoff := time.Now().Add(-ignoreLast)

    type SubprocessResponse struct {
        HashesList []string
        SimsList   []float64
        Report     string
    }

    fmt.Printf("[EXEC] Fetching suggested videos for `%s` ...\n", videoHash)
    start := time.Now()
    response, err := pyworker.ExecOutput[SubprocessResponse](
        "-m", "cmd.getSimilarVideos",
        "--target", videoHash,
        "--model-path", tfidfMatrixPath,
    )
    if err != nil {
        return handleServerError(c, 500, "Python subprocess failed", err)
    }
    tt := time.Since(start).Seconds()
    fmt.Printf("[EXEC] Done. Took %.2f sec\n", tt)
    fmt.Printf("[EXEC] REPORT: %s\n", response.Report)

    vids, err := getFilteredVideos(db_path, stateStore)
    if err != nil {
        return handleServerError(c, 500, "Unable to read videos table", err)
    }
    filteredMap := make(map[string]schemas.VideoData, len(vids))
    for _, vd := range vids {
        filteredMap[vd.Hash] = vd
    }

    interactions, err := db.GetCachedInteractions(db_path, 15, 3)
    if err != nil {
        return handleServerError(c, 500, "Unable to read interactions table", err)
    }

    const poolSize = 128
    type cand struct {
        video    schemas.VideoData
        simScore float64
        total    float64
    }
    candidates := make([]cand, 0, poolSize)

    for idx, hsh := range response.HashesList {
        if len(candidates) >= poolSize {
            break
        }
        if hsh == videoHash {
            continue
        }
        vd, ok := filteredMap[hsh]
        if !ok {
            continue
        }
        // Filter recently viewed
        if inter, hasInter := interactions[hsh]; hasInter && inter.LastViewed != "" {
            if t, parseErr := time.Parse("2006-01-02T15:04:05", inter.LastViewed); parseErr == nil && t.After(cutoff) {
                continue
            }
        }

        simScore := response.SimsList[idx]

        // Popularity score: f(x) = x / (x + 20), so popularity=20 → 0.5
        var popScore float64
        if inter, ok := interactions[hsh]; ok {
            popRaw := inter.GetUserPopularity()
            popScore = popRaw / (popRaw + 20.0)
        }

        // Platform score: f(x) = x / (x + 10000), so 10K views → 0.5
        platRaw := float64(vd.Views + vd.Likes*3)
        platScore := platRaw / (platRaw + 10000.0)

        candidates = append(candidates, cand{
            video:    vd,
            simScore: simScore,
            total:    simScore + popScore + platScore,
        })
    }

    slices.SortFunc(candidates, func(a, b cand) int {
        if a.total > b.total { return -1 }
        if a.total < b.total { return 1 }
        return 0
    })

    videos := make([]schemas.VideoData, len(candidates))
    simScores   := make(map[string]float64, len(candidates))
    totalScores := make(map[string]float64, len(candidates))
    for i, cd := range candidates {
        videos[i] = cd.video
        simScores[cd.video.Hash]   = cd.simScore
        totalScores[cd.video.Hash] = cd.total
    }

    type Reply struct {
        TimeTaken   float64             `json:"time_taken"`
        Videos      []schemas.VideoData `json:"videos"`
        SimScores   map[string]float64  `json:"sim_scores"`
        TotalScores map[string]float64  `json:"total_scores"`
    }
    return c.JSON(200, Reply{
        TimeTaken:   tt,
        Videos:      videos,
        SimScores:   simScores,
        TotalScores: totalScores,
    })
}

// ECHO_get_item_counts — batch video-count lookup for a list of actor or studio names
func ECHO_get_item_counts(c echo.Context, db_path string, stateStore *config.AppStateStore) error {
    var req struct {
        Type  string   `json:"type"`
        Names []string `json:"names"`
    }
    if err := StrictBind(c, &req); err != nil {
        return err
    }

    vids, err := getFilteredVideos(db_path, stateStore)
    if err != nil {
        return handleServerError(c, 500, "Unable to read videos table", err)
    }

    nameSet := make(map[string]struct{}, len(req.Names))
    counts  := make(map[string]int,     len(req.Names))
    for _, n := range req.Names {
        key := strings.ToLower(n)
        nameSet[key] = struct{}{}
        counts[key]  = 0
    }

    for _, vd := range vids {
        if req.Type == "actor" {
            for _, act := range vd.Actors {
                key := strings.ToLower(act)
                if _, ok := nameSet[key]; ok {
                    counts[key]++
                }
            }
        } else {
            key := strings.ToLower(vd.Studio)
            if _, ok := nameSet[key]; ok {
                counts[key]++
            }
        }
    }

    return c.JSON(200, map[string]any{"counts": counts})
}
