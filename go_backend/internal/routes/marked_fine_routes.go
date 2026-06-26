package routes

import (
    "log"
    "os"
    "path/filepath"
    "strings"
    "sync"

    "github.com/labstack/echo/v4"
)

var markedFineMu sync.RWMutex

func markedFinePath(appDataDir string) string {
    return filepath.Join(appDataDir, "marked_fine.txt")
}

func readMarkedFine(appDataDir string) ([]string, error) {
    markedFineMu.RLock()
    defer markedFineMu.RUnlock()

    data, err := os.ReadFile(markedFinePath(appDataDir))
    if os.IsNotExist(err) {
        return []string{}, nil
    }
    if err != nil {
        return nil, err
    }

    hashes := []string{}
    for _, line := range strings.Split(string(data), "\n") {
        h := strings.TrimSpace(line)
        if h != "" {
            hashes = append(hashes, h)
        }
    }
    return hashes, nil
}

func writeMarkedFine(appDataDir string, hashes []string) error {
    markedFineMu.Lock()
    defer markedFineMu.Unlock()
    return os.WriteFile(markedFinePath(appDataDir), []byte(strings.Join(hashes, "\n")+"\n"), 0644)
}

func ECHO_marked_fine_get(c echo.Context, appDataDir string) error {
    hashes, err := readMarkedFine(appDataDir)
    if err != nil {
        return handleServerError(c, 500, "Unable to read marked-fine file", err)
    }
    log.Printf("[marked-fine] GET returning %d hashes: %v", len(hashes), hashes)
    return c.JSON(200, map[string][]string{"hashes": hashes})
}

func ECHO_marked_fine_add(c echo.Context, appDataDir string) error {
    hash := c.Param("hash")
    hashes, err := readMarkedFine(appDataDir)
    if err != nil {
        return handleServerError(c, 500, "Unable to read marked-fine file", err)
    }
    for _, h := range hashes {
        if h == hash {
            return c.NoContent(204) // already present
        }
    }
    hashes = append(hashes, hash)
    if err := writeMarkedFine(appDataDir, hashes); err != nil {
        return handleServerError(c, 500, "Unable to write marked-fine file", err)
    }
    return c.NoContent(204)
}

func ECHO_marked_fine_remove(c echo.Context, appDataDir string) error {
    hash := c.Param("hash")
    hashes, err := readMarkedFine(appDataDir)
    if err != nil {
        return handleServerError(c, 500, "Unable to read marked-fine file", err)
    }
    filtered := hashes[:0]
    for _, h := range hashes {
        if h != hash {
            filtered = append(filtered, h)
        }
    }
    if len(filtered) == len(hashes) {
        return c.NoContent(204) // wasn't present
    }
    if err := writeMarkedFine(appDataDir, filtered); err != nil {
        return handleServerError(c, 500, "Unable to write marked-fine file", err)
    }
    return c.NoContent(204)
}
