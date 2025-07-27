// build: go build -ldflags="-s -w" -o main.exe main.go
package main

import (
	"os"
	"strings"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"cpv_backend/routes"
)

func NoCacheMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		err := next(c)
		path := c.Request().URL.Path
		if strings.HasSuffix(path, ".html") || strings.HasSuffix(path, ".js") || strings.HasSuffix(path, ".css") {
			c.Response().Header().Set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate")
			c.Response().Header().Set("Pragma", "no-cache")
			c.Response().Header().Set("Expires", "0")
		}
		return err
	}
}

// #region - MAIN ------------------------------------------------------------------------------------------------------

func main() {

	// Get config variables
	// PREVIEW_MEDIA_DIR, ACTOR_INFO_DIR, SUBTITLE_FOLDERS, TFIDF_MODEL_PATH, DATETIME_FORMAT
	config := GetConfig("../config.yaml")

	// d, _ := json.MarshalIndent(config, "", "    ")
	// fmt.Println(reflect.TypeOf(d))
	// fmt.Println(string(d))

	// Echo instance
	e := echo.New()

	// Use NoCache Middleware
	if os.Getenv("MY_ENV_VAR") == "1" {
		e.Use(NoCacheMiddleware)
	}

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Include routes
	routes.IncludeMediaRoutes( 	  e.Group("/media"))
	routes.IncludeApiRoutes( 	  e.Group("/api"))
	routes.IncludeQueryRoutes( 	  e.Group("/api/query"))
	routes.IncludeInteractRoutes( e.Group("/api/interact"))

	// hello there
	e.GET("/api/hello-there", func(c echo.Context) error {
		return c.String(200, "General Kenobi!")
	})

	// Simple text endpoint
	e.GET("/api/get-port", func(c echo.Context) error {
		return c.String(200, "69 probs idgaf")
	})

	// Simple JSON endpoint TODO: remove
	e.GET("/test/json", func(c echo.Context) error {
		return c.JSON(200, map[string]string{"message": "Hello, JSON response"})
	})

	// Static folders
	e.Static("/", "../frontend")

	e.Static("/static/preview-media", config.PreviewMediaDir)
	e.Static("/static/actor-store", config.ActorInfoDir)

	e.Logger.Fatal(e.Start(":8080"))

}
