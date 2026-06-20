//	BUILD (from project root)
//
// Windows: go build -C go_backend -ldflags="-s -w" -o ..\bin\CandyPopVideo.exe .
// Linux:   go build -C go_backend -ldflags="-s -w" -o ../CandyPopVideo
package main

import (
    "flag"
    "fmt"
    "log"
    "strings"

    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"

    "cpv_backend/internal/config"
    "cpv_backend/internal/db"
    "cpv_backend/internal/routes"
)

var (
    devMode    = flag.Bool("dev", false, "use dev mode")
    serverPort = flag.Int("port", 8010, "server port")
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

    store, err := config.NewConfigStore()
    if err != nil {
        log.Fatalf("Failed to initialize config: %v", err)
    }
    cfg := store.Current()

    if err := db.InitDB(cfg.DBPath); err != nil {
        log.Fatalf("Failed to initialize database: %v", err)
    }

    e := echo.New()

    e.Use(middleware.LoggerWithConfig(middleware.LoggerConfig{
        Format: "${method} ${uri} ${status} ${latency_human}\n",
    }))
    e.Use(middleware.Recover())

    if *devMode {
        fmt.Println("[GO] Using NoCacheMiddleware")
        e.Use(NoCacheMiddleware)
    }

    routes.IncludeMediaRoutes(    e.Group("/media"),         cfg.DBPath, cfg.PreviewMediaDir, cfg.SubtitleFolders)
    routes.IncludeApiRoutes(      e.Group("/api"),           cfg.DBPath, cfg.ActorInfoDir)
    routes.IncludeQueryRoutes(    e.Group("/api/query"),     cfg.DBPath, cfg.TfidfMatrixPath)
    routes.IncludeInteractRoutes( e.Group("/api/interact"),  cfg.DBPath)
    routes.IncludeDashboardRoutes(e.Group("/api/dashboard"), store)
    routes.IncludeRenameRoutes(   e.Group("/api"),           store)
    routes.IncludeConfigRoutes(   e.Group("/api"),           store)

    e.GET("/hello-there", func(c echo.Context) error {
        return c.String(200, "General Kenobi!")
    })

    e.GET("/api/get-port", func(c echo.Context) error {
        return c.String(200, (string)(*serverPort))
    })

    e.Static("/assets", "frontend/dist/assets")
    e.File("/favicon.svg", "frontend/dist/favicon.svg")

    e.Static("/static/preview-media", cfg.PreviewMediaDir)
    e.Static("/static/actor-store", cfg.ActorInfoDir)

    e.GET("/*", func(c echo.Context) error {
        return c.File("frontend/dist/index.html")
    })

    addr := fmt.Sprintf(":%d", *serverPort)
    e.Logger.Fatal(e.Start(addr))

}
