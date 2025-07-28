package routes

import (
	"encoding/json"
	"log"
	"time"

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
		
		var q schemas.SearchQuery
		if err := StrictBind(c, &q); err != nil {
			return c.String(400, "Invalid JSON: "+err.Error())
		}

		// get vidoes
		mp, err := db.GetCachedVideos(db_path, 15, 3)
		if err != nil {
			log.Printf("🚨🚨 ERROR 🚨🚨: %v", err)
			return c.String(500, "Unable to read table")
		}

		// get search results TODO: Replace with search logic
		start := time.Now()
		results := []schemas.VideoData{}
		i := 0
		for _, vd := range mp {
			results = append(results, vd)
			if i++; i >= 20 {
				break
			}
		}
		
		return c.JSON(200, map[string]any{
			"search_results": results,
			"videos_filtered_count": i,
			"word_cloud": nil,
			"time_taken": float64(time.Since(start).Microseconds())/1000,
		})
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
			log.Printf("🚨🚨 ERROR 🚨🚨: %v", err)
			return c.String(500, "Unable to read table: "+err.Error())
		}
		
		// get values
		videos_list := []schemas.VideoData{}
		for _, vd := range mp {
			videos_list = append(videos_list, vd)
		}

		// get catalogue
		start := time.Now()
		cat, err := query.GetCatalogue(videos_list, q)
		if err != nil {
			log.Printf("🚨🚨 ERROR 🚨🚨: %v", err)
			return c.String(500, "GetCatalogue failed:"+err.Error())
		}
		cat.TimeTakenMS = float64(time.Since(start).Microseconds())/1000
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
