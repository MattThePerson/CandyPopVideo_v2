package routes

import "github.com/labstack/echo/v4"

func IncludeApiRoutes(e *echo.Group) {

	// get videodata
	e.GET("/get/video-data/:hash", func(c echo.Context) error {
		hash := c.Param("hash")
		return c.JSON(200, map[string]string{"hash": hash})
	})

	// GET RANDOM VIDEO
	e.GET("/get/random-video-hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	// GET RANDOM SPOTLIGHT VIDEO
	e.GET("/get/random-spotlight-video-hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	// GET CURATED COLLECTIONS
	e.GET("/get/curated-collections", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	// GET MOVIE
	e.GET("/get/movie/:movie_title", func(c echo.Context) error {
		movie_title := c.Param("movie_title")
		return c.String(501, "Not implemented: "+movie_title)
	})

	// GET MOVIE SERIES
	e.GET("/get/movie-series/:movie_series", func(c echo.Context) error {
		movie_series := c.Param("movie_series")
		return c.String(501, "Not implemented: "+movie_series)
	})

	// GET LINE
	e.GET("/get/line/:line", func(c echo.Context) error {
		line := c.Param("line")
		return c.String(501, "Not implemented: "+line)
	})

	// GET ACTOR
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
