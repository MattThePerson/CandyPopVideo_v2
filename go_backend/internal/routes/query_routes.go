package routes

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/labstack/echo/v4"

	"cpv_backend/internal/db"
	"cpv_backend/internal/query"
	"cpv_backend/internal/schemas"
)

// Strictly binds recieved JSON to a struct
func StrictBind(c echo.Context, s any) error {

	decoder := json.NewDecoder(c.Request().Body)
	decoder.DisallowUnknownFields()

	if err := decoder.Decode(&s); err != nil {
		return c.String(400, "Invalid JSON: "+err.Error())
	}

	return nil
}

func IncludeQueryRoutes(e *echo.Group, db_path string) {

	e.POST("/search-videos", 		func(c echo.Context) error { return ECHO_search_videos(c, db_path) })
	e.POST("/get/catalogue", 		func(c echo.Context) error { return ECHO_get_catalogue(c, db_path) })

	e.GET("/get/similar-videos/:video_hash", 	func(c echo.Context) error { return ECHO_get_similar_videos(c, db_path) })
	e.GET("/get/similar-actors/:name",   		func(c echo.Context) error { return ECHO_get_similar_actors(c) })
	e.GET("/get/similar-studios/:name", 		func(c echo.Context) error { return ECHO_get_similar_studios(c) })

}


// ECHO_search_videos
// /:video_hash/:start_from/:limit
func ECHO_search_videos(c echo.Context, db_path string) error {
	
	// query
	var q schemas.SearchQuery
	if err := StrictBind(c, &q); err != nil {
		return c.String(400, "Invalid JSON: "+err.Error())
	}

	// get vidoes
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		return handleServerError(c, 500, "Unable to read videos table", err)
	}
	vids := extractValuesFromMap(mp)

	// interactions
	i, err := db.ReadSerializedMapFromTable[schemas.VideoInteractions](db_path, "interactions")
	// i, err := db.GetCachedInteractions(db_path, 5, 1)
	if err != nil {
		return handleServerError(c, 500, "Unable to read interactions table", err)
	}

	// get search results
	results, err := query.FilterAndSortVideos(vids, q, i)
	if err != nil {
		return handleServerError(c, 500, "Unable to filter and sort videos", err)
	}

	// sort by search query (TF-IDF)
	if q.SearchString != "" {
		// 1: get list of similar hashes via subprocess
		// 2: sort search results by similarity score
	}
	
	return c.JSON(200, results)
}


// ECHO_get_catalogue
// ...
func ECHO_get_catalogue(c echo.Context, db_path string) error {
	var q schemas.CatalogueQuery
	if err := StrictBind(c, &q); err != nil {
		return c.String(400, "Invalid JSON: "+err.Error())
	}

	// get vidoes
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		return handleServerError(c, 500, "Unable to read videos table", err)
	}
	vids := extractValuesFromMap(mp)

	// get catalogue
	cat, err := query.GetCatalogue(vids, q)
	if err != nil {
		return handleServerError(c, 500, "Unable to get catalogue", err)
	}
	return c.JSON(200, cat)
}


// ECHO_get_similar_videos
// query/get/similar-videos/:video_hash/:start_from/:limit
func ECHO_get_similar_videos(c echo.Context, db_path string) error {
	video_hash := c.Param("video_hash")

	// unmarshal subprocess response
	type SubprocessResponse struct {
		HashesList	[]string
		SimsList 	[]float64
		Report 		string
	}
	
	// [subprocess] get similar videos
	fmt.Printf("[EXEC] Fetching similar videos for `%s` ...\n", video_hash)
	start := time.Now()
	response, err := execPythonSubprocess_Output[SubprocessResponse](
		"-m", "python_src.worker_scripts.getSimilarVideos",
		"-target", video_hash,
	)
	if err != nil {
		return handleServerError(c, 500, "Python subprocess failed", err)
	}
	tt := time.Since(start).Seconds()
	fmt.Printf("[EXEC] Done. Took %.2f sec\n", tt)
	fmt.Printf("[EXEC] REPORT: %s\n", response.Report)

	// fmt.Printf("SIMILAR HASHES:\n%v\n\n", response)
	
	// load vidoes
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		return handleServerError(c, 500, "Unable to read videos table", err)
	}
	
	// 
	videos := []schemas.VideoData{}
	sims := map[string]float64{}
	for idx, hsh := range response.HashesList {
		videos = append(videos, mp[hsh])
		sims[hsh] = response.SimsList[idx]
	}

	// Construct reply
	type Reply struct {
		TimeTaken	float64
		Videos 		[]schemas.VideoData
		SimScores 	map[string]float64
	}
	reply := Reply{
		TimeTaken: tt,
		Videos: videos,
		SimScores: sims,
	}
	
	return c.JSON(200, reply)
}

// ECHO_get_similar_actors
func ECHO_get_similar_actors(c echo.Context) error {
	return c.String(501, "Not implemented")
}

// ECHO_get_similar_studios
func ECHO_get_similar_studios(c echo.Context) error {
	return c.String(501, "Not implemented")
}

