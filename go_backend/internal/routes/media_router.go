package routes

import (
	"cpv_backend/internal/db"
	"cpv_backend/internal/schemas"

	"github.com/labstack/echo/v4"
)

func IncludeMediaRoutes(e *echo.Group, db_path string, preview_media_dir string) {

	//
	e.GET("/get/video/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 500, "Unable to get data for hash: "+video_hash, err)
		}
		return c.File(vd.Path)
	})

	//
	e.GET("/get/poster/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		// TODO: Check for preview thumbs
		poster_pth := preview_media_dir + "/0x" + video_hash + "/poster.png"
		// fmt.Println("POSTER: " + poster_pth)
		return c.File(poster_pth)
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
		// video_hash := c.Param("video_hash")
		return c.String(200, "Hopefully exists idk")
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
