package routes

import (
    "encoding/json"
    "os"
    "path/filepath"

    "github.com/labstack/echo/v4"
)

type CuratedSiteMeta struct {
    ID          string `json:"id"`
    Name        string `json:"name"`
    Description string `json:"description"`
}

func IncludeCuratedSitesRoutes(g *echo.Group, sitesDir string) {
    g.GET("/curated-sites", func(c echo.Context) error {
        return ECHO_get_curated_sites(c, sitesDir)
    })
}

func ECHO_get_curated_sites(c echo.Context, sitesDir string) error {
    entries, err := os.ReadDir(sitesDir)
    if os.IsNotExist(err) {
        return c.JSON(200, []CuratedSiteMeta{})
    }
    if err != nil {
        return handleServerError(c, 500, "Unable to read curated sites directory", err)
    }

    sites := []CuratedSiteMeta{}
    for _, entry := range entries {
        if !entry.IsDir() {
            continue
        }
        // Only include folders that have an index.html
        indexPath := filepath.Join(sitesDir, entry.Name(), "index.html")
        if _, err := os.Stat(indexPath); err != nil {
            continue
        }

        site := CuratedSiteMeta{
            ID:   entry.Name(),
            Name: entry.Name(),
        }

        // Optional meta.json for display name and description
        metaPath := filepath.Join(sitesDir, entry.Name(), "meta.json")
        if data, readErr := os.ReadFile(metaPath); readErr == nil {
            var meta struct {
                Name        string `json:"name"`
                Description string `json:"description"`
            }
            if json.Unmarshal(data, &meta) == nil {
                if meta.Name != "" {
                    site.Name = meta.Name
                }
                site.Description = meta.Description
            }
        }

        sites = append(sites, site)
    }
    return c.JSON(200, sites)
}
