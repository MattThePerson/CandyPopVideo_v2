package routes

import (
	"cpv_backend/internal/db"
	"cpv_backend/internal/schemas"
	"database/sql"
	"errors"
	"strconv"
	"strings"

	"github.com/labstack/echo/v4"
)

func IncludeInteractRoutes(e *echo.Group, db_path string) {


	e.GET("/get/:video_hash", 				func(c echo.Context) error { return ECHO_get_interactions(c, db_path) })
	
	// favourites
	e.GET("/favourites/check/:video_hash", 	func(c echo.Context) error { return ECHO_favs_check(c, db_path) })
	e.POST("/favourites/add/:video_hash", 					func(c echo.Context) error { return ECHO_fav_add(c, db_path) })
	e.POST("/favourites/remove/:video_hash", 				func(c echo.Context) error { return ECHO_fav_remove(c, db_path) })
	e.POST("/favourites/update-time/:video_hash/:new_date", func(c echo.Context) error { return ECHO_fav_update_time(c, db_path) })

	e.POST("/likes/add/:video_hash", 				func(c echo.Context) error { return ECHO_likes_add(c, db_path) })
	e.POST("/last-viewed/add/:video_hash", 			func(c echo.Context) error { return ECHO_last_viewed_add(c, db_path) })
	e.POST("/viewtime/add/:video_hash/:viewtime", 	func(c echo.Context) error { return ECHO_viewtime_add(c, db_path) })
	
	// markers
	e.POST("/markers/update/:video_hash", 	func(c echo.Context) error { return c.String(501, "Not implemented") })
	e.GET("/markers/get/:video_hash", 		func(c echo.Context) error { return c.String(501, "Not implemented") })

}



// ECHO_get_interactions
func ECHO_get_interactions(c echo.Context, db_path string) error {
	video_hash := c.Param("video_hash")
	inter, err := db.ReadSerializedRowFromTable[schemas.VideoInteractions](db_path, "interactions", video_hash)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		return handleServerError(c, 500, "Unable to read interactions row", err)
	}
	return c.JSON(200, inter)
}


// #region FAVOURITES

// ECHO_favs_check
func ECHO_favs_check(c echo.Context, db_path string) error {
	video_hash := c.Param("video_hash")
	inter, err := db.ReadSerializedRowFromTable[schemas.VideoInteractions](db_path, "interactions", video_hash)
	if errors.Is(err, sql.ErrNoRows) {
		c.JSON(200, false)
	} else if err != nil {
		return handleServerError(c, 500, "Unable to read from database", err)
	}
	return c.JSON(200, inter.IsFavourite)
}


// ECHO_fav_add
func ECHO_fav_add(c echo.Context, db_path string) error {
	return updateInteractionsTable(c, db_path, func(inter *schemas.VideoInteractions) error {
		
		if inter.IsFavourite {
			return c.String(400, "Video is already favourited")
		}
		inter.IsFavourite = true
		inter.FavouritedDate = getCurrentTime()

		return c.String(200, "Favourite aded")
	})
}

// ECHO_fav_remove
func ECHO_fav_remove(c echo.Context, db_path string) error {
	return updateInteractionsTable(c, db_path, func(inter *schemas.VideoInteractions) error {
		
		if !inter.IsFavourite {
			return c.String(400, "Video is already NOT favourited")
		}
		inter.IsFavourite = false
		inter.FavouritedDate = ""

		return c.String(200, "Favourite added")
	})
}


// ECHO_fav_remove
func ECHO_fav_update_time(c echo.Context, db_path string) error {
	return updateInteractionsTable(c, db_path, func(inter *schemas.VideoInteractions) error {
		
		new_date := c.Param("new_date")
		
		if !inter.IsFavourite {
			return c.String(400, "Video is not favourited")
		}

		new_date = strings.ReplaceAll(new_date, " ", "T")

		if !isValidDateTime(new_date) {
			return c.String(400, "New date is invalid: "+new_date)
		}

		inter.FavouritedDate = new_date

		return c.String(200, "Updated favourited date")
	})
}


// #region OTHER

func ECHO_likes_add(c echo.Context, db_path string) error {
	return updateInteractionsTable(c, db_path, func(inter *schemas.VideoInteractions) error {
		
		inter.Likes += 1

		return c.String(200, "Liked video ❤️")
	})
}

// ECHO_last_viewed_add
func ECHO_last_viewed_add(c echo.Context, db_path string) error {
	return updateInteractionsTable(c, db_path, func(inter *schemas.VideoInteractions) error {
		
		inter.LastViewed = getCurrentTime()

		return c.String(200, "Favourite added")
	})
}

// ECHO_viewtime_add
func ECHO_viewtime_add(c echo.Context, db_path string) error {
	return updateInteractionsTable(c, db_path, func(inter *schemas.VideoInteractions) error {
		
		viewtime, err := strconv.ParseFloat( c.Param("viewtime"), 64 )
		if err != nil {
			return handleServerError(c, 500, "Unable to parse float", err)
		}
		inter.Viewtime += viewtime
		
		// update views table
		err = db.InsertDataIntoTable(db_path, "views", map[string]any{
			"timestamp": getCurrentTime(),
			"video_hash": c.Param("video_hash"),
			"duration_sec": viewtime,
		})
		if err != nil {
			return err
		}

		return c.String(200, "Favourite aded")
	})
}


// #region HELPERS

func updateInteractionsTable(c echo.Context, db_path string, callback_func func(inter *schemas.VideoInteractions) error) error {
	video_hash := c.Param("video_hash")
	
	// read row from db
	inter, err := db.ReadSerializedRowFromTable[schemas.VideoInteractions](db_path, "interactions", video_hash)
	if err != nil && !errors.Is(err, sql.ErrNoRows) { // if no rows, use zero struct
		return handleServerError(c, 500, "Unable to read interactions row", err)
	}

	// exec callback
	err = callback_func(&inter)
	if err != nil {
		return err
	}

	// update db
	err = db.WriteSerializedRowToTable(db_path, "interactions", video_hash, inter)
	if err != nil {
		return handleServerError(c, 500, "Unable to write to interactions table", err)
	}
	
	return nil
}

