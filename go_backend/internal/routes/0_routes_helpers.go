package routes

import (
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/labstack/echo/v4"

	"cpv_backend/internal/config"
	"cpv_backend/internal/db"
	"cpv_backend/internal/query"
	"cpv_backend/internal/schemas"
)

// getFilteredVideos loads the cached video slice with the global content filter applied.
func getFilteredVideos(db_path string, stateStore *config.AppStateStore) ([]schemas.VideoData, error) {
	mp, err := db.GetCachedVideos(db_path, 15, 3)
	if err != nil {
		return nil, err
	}
	return query.ApplyGlobalFilter(extractValuesFromMap(mp), stateStore.GetFilter()), nil
}

func extractValuesFromMap[S any](mp map[string]S) []S {
	values := []S{}
	for _, v := range mp {
		values = append(values, v)
	}
	return values
}

func handleServerError(c echo.Context, status int, msg string, err error) error {
	server_prefix := "🚨🚨 ERROR 🚨🚨: "
	route := c.Path()
	err_msg := fmt.Sprintf("%s: %s", msg, err.Error())
	log.Printf("%s [%s] %s", server_prefix, route, err_msg)
	return c.String(status, err_msg)
}

func getVideoMediaDir(media_dir string, video_hash string) string {
	return media_dir + "/preview/0x" + video_hash
}



func getPreviewThumbnail(vid_media_dir string, large_thumbs bool) (string, error) {

	// if prevthumb not exist
	var prev_thumbs_dir = vid_media_dir + "/previewthumbs"
	entries, err := os.ReadDir(prev_thumbs_dir)
	if err != nil {
		return "", err
	}
	if len(entries) < 10 {
		return "", errors.New("not enough images in preview media dir")
	}
	
	// get seeded random file
	var res = "360"
	if large_thumbs {
		res = "1080"
	}

	// get thumbs
	var thumbs []string
	for _, e := range entries {
		if strings.Contains(e.Name(), res) {
			thumbs = append(thumbs, fmt.Sprintf("%s/%s", prev_thumbs_dir, e.Name()))
		}
	}
	var idx = int(time.Now().Unix() % 5)
	return thumbs[idx], nil
}


func absDiff(a, b int64) int64 {
	if (a - b) > 0 {
		return a - b
	}
	return b - a
}


func getCurrentTime() string {
	return time.Now().Format("2006-01-02T15:04:05")
}

func isValidDateTime(str string) bool {
    layout := "2006-01-02T15:04:05"
    _, err := time.Parse(layout, str)
    return err == nil
}



// formatStringForIntComparability
func formatStringForIntComparability(input string) string {

	// remove grammar
	for _, char := range []string{".", ",", ":", ";", "'", "*", "!", "_", "-"} {
		input = strings.ReplaceAll(input, char, "")
	}

	// split into parts
	parts_hold := strings.Split(strings.ToLower(input), " ")
	parts := []string{}
	for _, p := range parts_hold {
		if p != "" {
			parts = append(parts, p)
		}
	}

	// process parts
	for idx, p := range parts {
		num, err := strconv.Atoi(p)
		if err == nil {
			parts[idx] = fmt.Sprintf("!%60d", num)
		}
	}
	return strings.Join(parts, " ")
}


