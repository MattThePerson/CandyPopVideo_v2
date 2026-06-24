package routes

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/MattThePerson/string_parser"
	"github.com/labstack/echo/v4"

	"cpv_backend/internal/config"
	"cpv_backend/internal/db"
	"cpv_backend/internal/scanner"
	"cpv_backend/internal/schemas"
)

func IncludeRenameRoutes(e *echo.Group, store *config.ConfigStore) {
    e.POST("/rename/:hash", func(c echo.Context) error { return ECHO_rename_video(c, store.Current()) })
}

type renameRequest struct {
    NewStem string `json:"new_stem"`
}

type renameResponse struct {
    OldPath     string `json:"old_path"`
    NewPath     string `json:"new_path"`
    OldFilename string `json:"old_filename"`
    NewFilename string `json:"new_filename"`
}

// Windows + POSIX illegal filename characters.
const illegalChars = `\/:*?"<>|`

func validateStem(stem string) error {
    if strings.TrimSpace(stem) == "" {
        return fmt.Errorf("filename cannot be empty")
    }
    for _, ch := range illegalChars {
        if strings.ContainsRune(stem, ch) {
            return fmt.Errorf("filename contains illegal character: %c", ch)
        }
    }
    return nil
}

func ECHO_rename_video(c echo.Context, cfg config.Config) error {
    hash := c.Param("hash")

    var req renameRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
    }

    newStem := strings.TrimSpace(req.NewStem)
    if err := validateStem(newStem); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
    }

    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](cfg.DBPath, "videos", hash)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{"error": "could not read video from database"})
    }

    oldPath := vd.Path
    ext := filepath.Ext(oldPath)
    newFilename := newStem + ext
    newPath := filepath.Join(filepath.Dir(oldPath), newFilename)

    // No-op if the name hasn't changed.
    if oldPath == newPath {
        return c.JSON(http.StatusOK, renameResponse{
            OldPath: oldPath, NewPath: newPath,
            OldFilename: vd.Filename, NewFilename: newFilename,
        })
    }

    // Rename the file on disk.
    if err := os.Rename(oldPath, newPath); err != nil {
        return c.JSON(http.StatusConflict, map[string]string{
            "error": fmt.Sprintf("could not rename file: %v", err),
            "code":  "rename_failed",
        })
    }

    // Update path-derived fields.
    oldFilename := vd.Filename
    vd.Path = newPath
    vd.Filename = newFilename
    rel, relErr := filepath.Rel(vd.ParentDir, newPath)
    if relErr != nil {
        rel = newFilename
    }
    vd.PathRelative = rel

    parser := string_parser.NewStringParserFromList(cfg.SceneFilenameFormats)
    scanner.GetFileMetadata(newPath, &vd, parser, true)
    // _, cleanStem := scanner.ExtractTags(newStem)
    // if vd.Title == "" && vd.SceneTitle == "" {
    //     vd.Title = cleanStem
    // }
    vd.TagsFromPath = scanner.ExtractPathTags(&vd)
    scanner.RebuildTags(&vd)

    // Persist to DB. On failure, revert the file rename to keep fs and DB in sync.
    if err := db.WriteVideoRow(cfg.DBPath, hash, vd); err != nil {
        if revertErr := os.Rename(newPath, oldPath); revertErr != nil {
            log.Printf("[RENAME] CRITICAL: DB write failed and rename-back failed: %v", revertErr)
            return c.JSON(http.StatusInternalServerError, map[string]string{
                "error": fmt.Sprintf("database update failed and rename could not be reverted — file is now at: %s", newPath),
                "code":  "critical_failure",
            })
        }
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "database update failed; file rename has been undone",
            "code":  "db_failed",
        })
    }

    db.InvalidateCache()
    writeRenameLog(oldPath, newPath)

    return c.JSON(http.StatusOK, renameResponse{
        OldPath: oldPath, NewPath: newPath,
        OldFilename: oldFilename, NewFilename: newFilename,
    })
}

// writeRenameLog appends a line to .logs/renames.log (relative to cwd = project root).
func writeRenameLog(oldPath, newPath string) {
    if err := os.MkdirAll(".logs", 0755); err != nil {
        log.Printf("[RENAME] Failed to create .logs dir: %v", err)
        return
    }
    f, err := os.OpenFile(".logs/renames.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
    if err != nil {
        log.Printf("[RENAME] Failed to open rename log: %v", err)
        return
    }
    defer f.Close()
    fmt.Fprintf(f, "[%s] RENAME: %q -> %q\n", time.Now().UTC().Format(time.RFC3339), oldPath, newPath)
}
