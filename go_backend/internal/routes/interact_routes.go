package routes

import (
    "cpv_backend/internal/db"
    "cpv_backend/internal/schemas"
    "database/sql"
    "errors"
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

    e.POST("/likes/add/:video_hash",        func(c echo.Context) error { return ECHO_likes_add(c, db_path) })
    e.POST("/viewing/add/:video_hash",      func(c echo.Context) error { return ECHO_viewing_add(c, db_path) })
	
	// markers
	e.POST("/markers/update/:video_hash", 	func(c echo.Context) error { return c.String(501, "Not implemented") })
	e.GET("/markers/get/:video_hash", 		func(c echo.Context) error { return c.String(501, "Not implemented") })

}



// ECHO_get_interactions
func ECHO_get_interactions(c echo.Context, db_path string) error {
	video_hash := c.Param("video_hash")
	inter, err := db.ReadInteractionsRow(db_path, video_hash)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		return handleServerError(c, 500, "Unable to read interactions row", err)
	}
	return c.JSON(200, inter)
}


// #region FAVOURITES

// ECHO_favs_check
func ECHO_favs_check(c echo.Context, db_path string) error {
	video_hash := c.Param("video_hash")
	inter, err := db.ReadInteractionsRow(db_path, video_hash)
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

// ECHO_viewing_add records a completed playback section. The frontend sends
// the section's start position and duration; this handler updates interactions
// (last_viewed + cumulative viewtime) and appends a row to the viewings log.
// Sections shorter than 1.5s are silently ignored.
func ECHO_viewing_add(c echo.Context, db_path string) error {
    hash := c.Param("video_hash")

    var body struct {
        TimeStart   float64 `json:"time_start"`
        DurationSec float64 `json:"duration_sec"`
    }
    if err := c.Bind(&body); err != nil {
        return c.JSON(400, map[string]string{"error": "invalid body"})
    }
    if body.DurationSec < 1.5 {
        return c.String(200, "section too short")
    }

    inter, err := db.ReadInteractionsRow(db_path, hash)
    if err != nil && !errors.Is(err, sql.ErrNoRows) {
        return handleServerError(c, 500, "Unable to read interactions", err)
    }
    inter.LastViewed = getCurrentTime()
    inter.Viewtime += body.DurationSec
    if err := db.WriteInteractionsRow(db_path, hash, inter); err != nil {
        return handleServerError(c, 500, "Unable to write interactions", err)
    }
    db.InvalidateInteractionsCache()

    if err := db.InsertDataIntoTable(db_path, "viewings", map[string]any{
        "video_hash":   hash,
        "datetime":     getCurrentTime(),
        "time_start":   body.TimeStart,
        "duration_sec": body.DurationSec,
    }); err != nil {
        return handleServerError(c, 500, "Unable to insert viewing", err)
    }

    return c.String(200, "viewing recorded")
}


// #region HELPERS

func updateInteractionsTable(c echo.Context, db_path string, callback_func func(inter *schemas.VideoInteractions) error) error {
	video_hash := c.Param("video_hash")
	
	// read row from db
	inter, err := db.ReadInteractionsRow(db_path, video_hash)
	if err != nil && !errors.Is(err, sql.ErrNoRows) { // if no rows, use zero struct
		return handleServerError(c, 500, "Unable to read interactions row", err)
	}

	// exec callback
	err = callback_func(&inter)
	if err != nil {
		return err
	}

	// update db
	err = db.WriteInteractionsRow(db_path, video_hash, inter)
	if err != nil {
		return handleServerError(c, 500, "Unable to write to interactions table", err)
	}
	db.InvalidateInteractionsCache()
	return nil
}

