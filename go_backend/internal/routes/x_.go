package routes

import (
	"log"

	"github.com/labstack/echo/v4"
)

func extractValuesFromMap[S any](mp map[string]S) []S {
	values := []S{}
	for _, v := range mp {
		values = append(values, v)
	}
	return values
}

func handleServerError(c echo.Context, status int, msg string, err error) error {
	server_prefix := "🚨🚨 ERROR 🚨🚨: "
	err_msg := msg + ": " + err.Error()
	log.Println(server_prefix + err_msg)
	return c.String(status, err_msg)
}
