package routes

import (
	"math/rand"

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

		// get videos
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
		return c.String(501, "Not implemented")
	})


	// Get curated collections
	e.GET("/get/curated-collections", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})


	// Get videos from movie
	e.GET("/get/movie/:movie_title", func(c echo.Context) error {
		movie_title := c.Param("movie_title")
		return c.String(501, "Not implemented: "+movie_title)
	})


	// Get videos from movie series
	e.GET("/get/movie-series/:movie_series", func(c echo.Context) error {
		movie_series := c.Param("movie_series")
		return c.String(501, "Not implemented: "+movie_series)
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

	// TEMP TODO: Find better solution

	// GET VIDEO COUNT
	e.GET("/get/video-count", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})


	// GET ACTOR VIDEO COUNT
	e.GET("/get/actor-video-count/:name", func(c echo.Context) error {
		name := c.Param("name")
		return c.String(501, "Not implemented: "+name)
	})


	// GET ACTOR VIDEO COUNT
	e.GET("/get/studio-video-count/:name", func(c echo.Context) error {
		name := c.Param("name")
		return c.String(501, "Not implemented: "+name)
	})

}
