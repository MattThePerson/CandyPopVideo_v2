package routes

import (
	"cpv_backend/internal/db"
	"cpv_backend/internal/schemas"

	"github.com/labstack/echo/v4"
)

func IncludeInteractRoutes(e *echo.Group, db_path string) {


	// Get all interactions
	e.GET("/get/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		inter, err := db.ReadSerializedRowFromTable[schemas.VideoInteractions](db_path, "interactions", video_hash)
		if err != nil {
			handleServerError(c, 500, "Unable to read interactions row", err)
		}
		return c.JSON(200, inter)
	})


	/* GET ROUTES */
	
	e.GET("/favourites/check/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})


	/* POST ROUTES */

	e.POST("/favourites/add/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	e.POST("/favourites/remove/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	e.POST("/likes/add/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	e.POST("/last-viewed/add/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})
	
	e.POST("/viewtime/add/:video_hash/:viewtime", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})
	

	/* MARKERS */

	e.POST("/markers/update/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

	e.GET("/markers/get/:video_hash", func(c echo.Context) error {
		return c.String(501, "Not implemented")
	})

}
