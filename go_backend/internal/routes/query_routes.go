package routes

import (
    "encoding/json"
    "fmt"
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

func IncludeQueryRoutes(e *echo.Group, db_path string, tfidfMatrixPath string, stateStore *config.AppStateStore) {
    e.POST("/search-videos",                    func(c echo.Context) error { return ECHO_search_videos(c, db_path, stateStore) })
    e.POST("/get/catalogue",                    func(c echo.Context) error { return ECHO_get_catalogue(c, db_path, stateStore) })
    e.GET("/get/similar-videos/:video_hash",    func(c echo.Context) error { return ECHO_get_similar_videos(c, db_path, tfidfMatrixPath, stateStore) })
    e.GET("/get/similar-actors/:name",          func(c echo.Context) error { return ECHO_get_similar_actors(c) })
    e.GET("/get/similar-studios/:name",         func(c echo.Context) error { return ECHO_get_similar_studios(c) })
}


// ECHO_search_videos
func ECHO_search_videos(c echo.Context, db_path string, stateStore *config.AppStateStore) error {
    var q schemas.SearchQuery
    if err := StrictBind(c, &q); err != nil {
        return c.String(400, "Invalid JSON: "+err.Error())
    }

    // TEMP
    bts, _ := json.MarshalIndent(&q, "", "  ")
    fmt.Printf("search_query:\n%s\n\n", bts)

    vids, err := getFilteredVideos(db_path, stateStore)
    if err != nil {
        return handleServerError(c, 500, "Unable to read videos table", err)
    }

    i, err := db.ReadSerializedMapFromTable[schemas.VideoInteractions](db_path, "interactions")
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
func ECHO_get_similar_actors(c echo.Context) error {
    return c.String(501, "Not implemented")
}

// ECHO_get_similar_studios
func ECHO_get_similar_studios(c echo.Context) error {
    return c.String(501, "Not implemented")
}
