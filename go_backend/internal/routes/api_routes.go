package routes

import (
	"cmp"
	"fmt"
	"math"
	"math/rand"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/labstack/echo/v4"

	"cpv_backend/internal/db"
	"cpv_backend/internal/schemas"
)

func IncludeApiRoutes(e *echo.Group, db_path string) {

	e.GET("/get/video-data/:hash", 				func(c echo.Context) error { return ECHO_get_video_data(c, db_path) })
	e.GET("/get/random-video-hash", 			func(c echo.Context) error { return ECHO_get_random_hash(c, db_path) })
	e.GET("/get/random-spotlight-video-hash", 	func(c echo.Context) error { return ECHO_get_spotlight_hash(c, db_path) })
	e.GET("/get/movie/:movie_title", 			func(c echo.Context) error { return ECHO_get_movie(c, db_path) })
	e.GET("/get/movie-series/:movie_series", 	func(c echo.Context) error { return ECHO_get_movie_series(c, db_path) })
	e.GET("/get/line/:line", 					func(c echo.Context) error { return ECHO_get_line(c, db_path) })
	e.GET("/get/actor/:name", 					func(c echo.Context) error { return ECHO_get_actor(c, db_path) })
	e.GET("/get/actor-video-count/:name", 		func(c echo.Context) error { return ECHO_get_actor_vid_count(c, db_path) })
	e.GET("/get/studio-video-count/:name", 		func(c echo.Context) error { return ECHO_studio_vid_count(c, db_path) })
	e.GET("/get/curated-collections", 			func(c echo.Context) error { return ECHO_get_curated_collection(c) })
	
}




// ECHO_video
func ECHO_get_video_data(c echo.Context, db_path string) error {
	hash := c.Param("hash")
	vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", hash)
	if err != nil {
		handleServerError(c, 500, "Unable to get data for hash: "+hash, err)
	}
	
	return c.JSON(200, vd)
}


// ECHO_random
func ECHO_get_random_hash(c echo.Context, db_path string) error {
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	// get linked keys
	hashes := make([]string, 0, len(mp))
	for hsh := range mp {
		hashes = append(hashes, hsh)
	}
	if len(hashes) == 0 {
		return c.String(404, "No linked videos in db")
	}

	// random hash and return
	randHsh := hashes[rand.Intn(len(hashes))]
	return c.JSON(200, map[string]string{"hash": randHsh})
}


// ECHO_random
func ECHO_get_spotlight_hash(c echo.Context, db_path string) error {
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	// Generate seeded random hash
	tm := time.Now().Add(-6*time.Hour)
	seed_str := fmt.Sprintf("%d%d", tm.Year(), tm.YearDay())
	seed, _ := strconv.Atoi(seed_str)
	
	r := rand.New(rand.NewSource(int64(seed)))
	hsh := fmt.Sprintf("%012x", r.Intn(int(math.Pow(16, 12))))
	fmt.Println("[SPOTLIGHT] Generated random hash: "+hsh)
	
	// 
	hsh_i, _ := strconv.ParseInt(hsh, 16, 64)
	var closest_i int64 = 0
	for vhsh := range mp {
		vhsh_i, _ := strconv.ParseInt(vhsh, 16, 64)
		if absDiff(hsh_i, vhsh_i) < absDiff(hsh_i, closest_i) {
			closest_i = vhsh_i
			fmt.Printf("[SPOTLIGHT] New closest_i: %012x  (diff = %d)\n", closest_i, absDiff(hsh_i, closest_i))
		}
	}
	closest_hsh := fmt.Sprintf("%012x", closest_i)

	return c.String(200, closest_hsh)
}


// ECHO_movie
func ECHO_get_movie(c echo.Context, db_path string) error {
	movie_title := strings.ToLower(c.Param("movie_title"))
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	// get video list
	var vids = []schemas.VideoData{}
	for _, vd := range mp {
		if vd.MovieTitle != "" && strings.ToLower(vd.MovieTitle) == movie_title {
			vids = append(vids, vd)
		}
	}

	// sort vids
	slices.SortFunc(vids, func(a, b schemas.VideoData) int {
		if (a.DateReleased != b.DateReleased) {
			return cmp.Compare(a.DateReleased, b.DateReleased)
		}
		return cmp.Compare(a.Title, b.Title)
	})
	
	return c.JSON(200, vids)
}


// ECHO_movie
func ECHO_get_movie_series(c echo.Context, db_path string) error {
	movie_series := strings.ToLower(c.Param("movie_series"))
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	// get video list
	var vids = []schemas.VideoData{}
	for _, vd := range mp {
		if vd.MovieSeries != "" && strings.ToLower(vd.MovieSeries) == movie_series {
			vids = append(vids, vd)
		}
	}

	// sort videos
	slices.SortFunc(vids, func(a, b schemas.VideoData) int {
		if (a.DateReleased != b.DateReleased) {
			return cmp.Compare(a.DateReleased, b.DateReleased)
		}
		return cmp.Compare(a.Title, b.Title)
	})
	
	return c.JSON(200, vids)
}


// ECHO_get_line
func ECHO_get_line(c echo.Context, db_path string) error {
	line := strings.ToLower(c.Param("line"))
	if line == "" {
		return c.String(400, "Line cannot be empty")
	}
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	// get videos
	var vids = []schemas.VideoData{}
	for _, vd := range mp {
		if strings.ToLower(vd.Line) == line {
			vids = append(vids, vd)
		}
	}

	// sort videos
	slices.SortFunc(vids, func(a, b schemas.VideoData) int {
		if (a.DateReleased != b.DateReleased) {
			return cmp.Compare(a.DateReleased, b.DateReleased)
		}
		return cmp.Compare(a.DateAdded, b.DateAdded)
	})
	
	return c.JSON(200, vids)
}


// ECHO_get_actor
// params: name
func ECHO_get_actor(c echo.Context, db_path string) error {
	name := c.Param("name")

	// [subprocess] 
	data, err := execPythonSubprocess_Output[map[string]any](
		"-m", "python_src.worker_scripts.getActorInfo",
		"-name", name,
		"-redo", "false",
	)
	if err != nil {
		handleServerError(c, 500, "Python subprocess failed", err)
	}
	
	return c.JSON(200, data)
}


// ECHO_get_actor_vid_count
func ECHO_get_actor_vid_count(c echo.Context, db_path string) error {
	name := strings.ToLower(c.Param("name"))
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	count := 0
	for _, vd := range mp {
		for _, act := range vd.Actors {
			if strings.ToLower(act) == name {
				count++
			}
		}
	}
	return c.JSON(200, map[string]int{"video_count": count})
}


// ECHO_studio_vid_count
func ECHO_studio_vid_count(c echo.Context, db_path string) error {
	name := strings.ToLower(c.Param("name"))
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		handleServerError(c, 500, "Unable to read table", err)
	}

	count := 0
	for _, vd := range mp {
		if strings.ToLower(vd.Studio) == name || strings.ToLower(vd.Line) == name {
			count++
		}
	}
	return c.JSON(200, map[string]int{"video_count": count})
}


// ECHO_get_curated_collection
func ECHO_get_curated_collection(c echo.Context) error {
	return c.String(501, "Not implemented")
}










