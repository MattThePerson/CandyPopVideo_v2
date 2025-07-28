// build: go build -ldflags="-s -w" -o main.exe .
package main

import (
	"flag"
	"fmt"
	"strings"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"cpv_backend/internal/routes"
)

var (
	devMode 	= flag.Bool("dev", false, "use dev mode")
    serverPort	= flag.Int("port", 8010, "server port")
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

func main() {

	flag.Parse()

	// Get config variables
	var config Config = GetConfig("../config.yaml")

	// Echo instance
	e := echo.New()

	// Middleware
	e.Use(middleware.LoggerWithConfig(middleware.LoggerConfig{
		Format: "${method} ${uri} ${status} ${latency_human}\n",
	}))

	e.Use(middleware.Recover())

	if *devMode {
		fmt.Println("Using NoCacheMiddleware")
		e.Use(NoCacheMiddleware)
	}

	// Include routes
	routes.IncludeMediaRoutes( 	  e.Group("/media"), 		config.DBPath, config.PreviewMediaDir)
	routes.IncludeApiRoutes( 	  e.Group("/api"), 			config.DBPath)
	routes.IncludeQueryRoutes( 	  e.Group("/api/query"), 	config.DBPath)
	routes.IncludeInteractRoutes( e.Group("/api/interact"), config.DBPath)

	// hello there
	e.GET("/api/hello-there", func(c echo.Context) error {
		return c.String(200, "General Kenobi!")
	})

	// Simple text endpoint
	e.GET("/api/get-port", func(c echo.Context) error {
		return c.String(200, "6969 probably idgaf")
	})

	// Simple JSON endpoint TODO: remove
	e.GET("/test/json", func(c echo.Context) error {
		return c.JSON(200, map[string]string{"message": "Hello, JSON response"})
	})

	// Static folders
	e.Static("/", "../frontend")

	e.Static("/static/preview-media", config.PreviewMediaDir)
	e.Static("/static/actor-store", config.ActorInfoDir)

	addr := fmt.Sprintf(":%d", *serverPort)
	e.Logger.Fatal(e.Start(addr))

}
