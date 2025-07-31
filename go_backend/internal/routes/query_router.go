package routes

import (
	"encoding/json"

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


	// Get videodata
	e.POST("/search-videos", func(c echo.Context) error {
		
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

		// get search results TODO: Replace with search logic
		results, err := query.FilterAndSortVideos(vids, q, i)
		if err != nil {
			return handleServerError(c, 500, "Unable to filter and sort videos", err)
		}
		
		return c.JSON(200, results)
	})


	// Get catalogue
	e.POST("/get/catalogue", func(c echo.Context) error {
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
	})


	/* - TF-IDF ROUTES ------------------------------------------------------ */
	
	// Get ...
	e.GET("/get/similar-videos/{video_hash}/{start_from}/{limit}", func(c echo.Context) error {
		return c.String(501, "TF-IDF routes not yet implemented")
	})

	// Get ...
	e.GET("/get/similar-actors/{performer}", func(c echo.Context) error {
		return c.String(501, "TF-IDF routes not yet implemented")
	})

	// Get ...
	e.GET("/get/similar-studios/{studio}", func(c echo.Context) error {
		return c.String(501, "TF-IDF routes not yet implemented")
	})


}

