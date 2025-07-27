package routes

import "github.com/labstack/echo/v4"

func IncludeMediaRoutes(e *echo.Group) {

	//
	e.GET("/get/video/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/get/poster/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/ensure/teaser-small/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/ensure/teaser-thumbs-small/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/ensure/seek-thumbnails/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/get/subtitles/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/ensure/preview-thumbnails/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/get/poster-large/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/ensure/teaser-large/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

	//
	e.GET("/ensure/teaser-thumbs-large/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})

}
