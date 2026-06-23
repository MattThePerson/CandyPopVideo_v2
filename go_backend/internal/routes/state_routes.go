package routes

import (
    "cpv_backend/internal/config"

    "github.com/labstack/echo/v4"
)

func IncludeStateRoutes(e *echo.Group, stateStore *config.AppStateStore) {
    e.GET("/global-filter", func(c echo.Context) error { return ECHO_get_global_filter(c, stateStore) })
    e.POST("/global-filter", func(c echo.Context) error { return ECHO_set_global_filter(c, stateStore) })
}

func ECHO_get_global_filter(c echo.Context, stateStore *config.AppStateStore) error {
    return c.JSON(200, stateStore.GetFilter())
}

func ECHO_set_global_filter(c echo.Context, stateStore *config.AppStateStore) error {
    var f config.GlobalFilter
    if err := c.Bind(&f); err != nil {
        return c.JSON(400, map[string]string{"error": "invalid JSON"})
    }
    if err := stateStore.SetFilter(f); err != nil {
        return handleServerError(c, 500, "Failed to save filter", err)
    }
    return c.JSON(200, stateStore.GetFilter())
}
