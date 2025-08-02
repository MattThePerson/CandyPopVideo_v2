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

	// Get video data
	e.GET("/get/video-data/:hash", func(c echo.Context) error {
		hash := c.Param("hash")
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", hash)
		if err != nil {
			handleServerError(c, 500, "Unable to get data for hash: "+hash, err)
		}
		
		return c.JSON(200, vd)
	})


	// Get random video hash
	e.GET("/get/random-video-hash", func(c echo.Context) error {
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
	})


	// Get random spotlight video
	e.GET("/get/random-spotlight-video-hash", func(c echo.Context) error {
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
	})


	// Get videos from movie
	e.GET("/get/movie/:movie_title", func(c echo.Context) error {
		movie_title := strings.ToLower(c.Param("movie_title"))
		mp, err := db.GetCachedVideos(db_path, 15, 3)
		if err != nil {
			handleServerError(c, 500, "Unable to read table", err)
		}

		// get movie list
		var movies = []schemas.VideoData{}
		for _, vd := range mp {
			if vd.MovieTitle != "" && strings.ToLower(vd.MovieTitle) == movie_title {
				movies = append(movies, vd)
			}
		}

		// sort movies
		slices.SortFunc(movies, func(a, b schemas.VideoData) int {
			if (a.DateReleased != b.DateReleased) {
				return cmp.Compare(a.DateReleased, b.DateReleased)
			}
			return cmp.Compare(a.Title, b.Title)
		})
		
		return c.JSON(200, movies)
	})


	// Get videos from movie series
	e.GET("/get/movie-series/:movie_series", func(c echo.Context) error {
		movie_series := strings.ToLower(c.Param("movie_series"))
		mp, err := db.GetCachedVideos(db_path, 15, 3)
		if err != nil {
			handleServerError(c, 500, "Unable to read table", err)
		}

		// get movie list
		var movies = []schemas.VideoData{}
		for _, vd := range mp {
			if vd.MovieSeries != "" && strings.ToLower(vd.MovieSeries) == movie_series {
				movies = append(movies, vd)
			}
		}

		// sort movies
		slices.SortFunc(movies, func(a, b schemas.VideoData) int {
			if (a.DateReleased != b.DateReleased) {
				return cmp.Compare(a.DateReleased, b.DateReleased)
			}
			return cmp.Compare(a.Title, b.Title)
		})
		
		return c.JSON(200, movies)
	})


	// Get videos from line
	e.GET("/get/line/:line", func(c echo.Context) error {
		line := c.Param("line")
		return c.String(501, "Not implemented: "+line)
	})


	// Get actor info
	e.GET("/get/actor/:name", func(c echo.Context) error {
		name := c.Param("name")
		return c.String(501, "Not implemented: "+name)
	})


	// GET VIDEO COUNT
	// e.GET("/get/video-count", func(c echo.Context) error {
	// 	return c.String(501, "Not implemented")
	// })


	// GET ACTOR VIDEO COUNT
	e.GET("/get/actor-video-count/:name", func(c echo.Context) error {
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
	})


	// GET ACTOR VIDEO COUNT
	e.GET("/get/studio-video-count/:name", func(c echo.Context) error {
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
	})


	// Get curated collections
	e.GET("/get/curated-collections", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})


	
	
}
