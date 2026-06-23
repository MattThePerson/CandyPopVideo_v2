package routes

import (
    "io"
    "net/http"
    "os"
    "strings"

    "github.com/labstack/echo/v4"
    "gopkg.in/yaml.v3"

    "cpv_backend/internal/config"
)

func IncludeConfigRoutes(e *echo.Group, store *config.ConfigStore) {
    e.GET("/config",                  func(c echo.Context) error { return ECHO_config_get(c, store) })
    e.POST("/config/validate",        func(c echo.Context) error { return ECHO_config_validate(c, store) })
    e.POST("/config/save",            func(c echo.Context) error { return ECHO_config_save(c, store) })
    e.POST("/config/restore-defaults", func(c echo.Context) error { return ECHO_config_restore_defaults(c, store) })
}

// ─── Response types ───────────────────────────────────────────────────────────

type ConfigValidationResult struct {
    OK             bool     `json:"ok"`
    Errors         []string `json:"errors"`
    Warnings       []string `json:"warnings"`
    RequiresRestart bool    `json:"requires_restart"`
    Saved          bool     `json:"saved,omitempty"`
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

func validateConfigYAML(body []byte, store *config.ConfigStore) ConfigValidationResult {
    res := ConfigValidationResult{
        Errors:   []string{},
        Warnings: []string{},
    }

    // Parse YAML into Config struct.
    var cfg config.Config
    if err := yaml.Unmarshal(body, &cfg); err != nil {
        res.Errors = append(res.Errors, "invalid YAML: "+err.Error())
        return res
    }

    if strings.TrimSpace(cfg.PreviewMediaDir) == "" {
        res.Errors = append(res.Errors, "preview_media_dir is required")
    }

    // Check collection paths (warn if missing; skip !-prefixed exclusion paths).
    for collName, paths := range cfg.Collections {
        for _, p := range paths {
            trimmed := strings.TrimSpace(p)
            if strings.HasPrefix(trimmed, "!") {
                continue
            }
            if _, err := os.Stat(trimmed); err != nil {
                res.Warnings = append(res.Warnings,
                    "Collection '"+collName+"': path not found on disk: "+trimmed)
            }
        }
    }

    if len(res.Errors) == 0 {
        res.OK = true
        current := store.Current()
        if strings.TrimSpace(cfg.PreviewMediaDir) != current.PreviewMediaDir {
            res.RequiresRestart = true
        }
    }

    return res
}

// ─── Handlers ─────────────────────────────────────────────────────────────────

func ECHO_config_get(c echo.Context, store *config.ConfigStore) error {
    raw, err := store.RawYAML()
    if err != nil {
        return handleServerError(c, 500, "Failed to read config", err)
    }
    return c.Blob(http.StatusOK, "text/plain; charset=utf-8", []byte(raw))
}

func ECHO_config_validate(c echo.Context, store *config.ConfigStore) error {
    body, err := io.ReadAll(c.Request().Body)
    if err != nil {
        return handleServerError(c, 400, "Failed to read request body", err)
    }
    res := validateConfigYAML(body, store)
    return c.JSON(http.StatusOK, res)
}

func ECHO_config_save(c echo.Context, store *config.ConfigStore) error {
    body, err := io.ReadAll(c.Request().Body)
    if err != nil {
        return handleServerError(c, 400, "Failed to read request body", err)
    }

    res := validateConfigYAML(body, store)
    if !res.OK {
        return c.JSON(http.StatusUnprocessableEntity, res)
    }

    requiresRestart, err := store.WriteAndReload(body)
    if err != nil {
        return handleServerError(c, 500, "Failed to save config", err)
    }

    res.RequiresRestart = res.RequiresRestart || requiresRestart
    res.Saved = true
    return c.JSON(http.StatusOK, res)
}

func ECHO_config_restore_defaults(c echo.Context, store *config.ConfigStore) error {
    _, err := store.WriteAndReload(config.DefaultConfigBytes)
    if err != nil {
        return handleServerError(c, 500, "Failed to restore default config", err)
    }
    return c.JSON(http.StatusOK, map[string]bool{"saved": true})
}
