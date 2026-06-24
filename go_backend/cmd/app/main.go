//	BUILD (from project root)
//
// Windows: go build -C go_backend -ldflags="-s -w" -o ..\bin\CandyPopVideo.exe .
// Linux:   go build -C go_backend -ldflags="-s -w" -o ../CandyPopVideo
package main

import (
    "flag"
    "fmt"
    "log"
    "os"
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
    dataDir    = flag.String("data-dir", "", "override app data directory (default: OS user config dir)")
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

    store, err := config.NewConfigStore(*dataDir)
    if err != nil {
        log.Fatalf("Failed to initialize config: %v", err)
    }
    cfg := store.Current()

    if err := db.InitDB(cfg.DBPath); err != nil {
        log.Fatalf("Failed to initialize database: %v", err)
    }
    if err := db.MigrateInteractionsTable(cfg.DBPath); err != nil {
        log.Fatalf("Failed to migrate interactions table: %v", err)
    }
    if err := db.MigrateViewingsTable(cfg.DBPath); err != nil {
        log.Fatalf("Failed to migrate viewings table: %v", err)
    }

    stateStore := config.NewAppStateStore(cfg.AppDataDir)

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
    routes.IncludeApiRoutes(      e.Group("/api"),           cfg.DBPath, cfg.ActorInfoDir, store, stateStore)
    routes.IncludeQueryRoutes(    e.Group("/api/query"),     cfg.DBPath, cfg.TfidfMatrixPath, cfg.ActorProfilesPath, cfg.StudioProfilesPath, stateStore)
    routes.IncludeInteractRoutes( e.Group("/api/interact"),  cfg.DBPath)
    routes.IncludeDashboardRoutes(e.Group("/api/dashboard"), store)
    routes.IncludeRenameRoutes(   e.Group("/api"),           store)
    routes.IncludeConfigRoutes(   e.Group("/api"),           store)
    routes.IncludeStateRoutes(    e.Group("/api"),           stateStore)

    e.GET("/hello-there", func(c echo.Context) error {
        return c.String(200, "General Kenobi!")
    })

    e.GET("/api/get-port", func(c echo.Context) error {
        return c.String(200, (string)(*serverPort))
    })

    e.Static("/assets", "frontend/dist/assets")

    e.Static("/static/preview-media", cfg.PreviewMediaDir+"/preview")
    e.Static("/static/actor-store", cfg.ActorInfoDir)

    e.GET("/*", func(c echo.Context) error {
        filePath := "frontend/dist" + c.Request().URL.Path
        if _, err := os.Stat(filePath); err == nil {
            return c.File(filePath)
        }
        return c.File("frontend/dist/index.html")
    })

    addr := fmt.Sprintf(":%d", *serverPort)
    e.Logger.Fatal(e.Start(addr))

}
