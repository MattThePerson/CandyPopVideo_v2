package routes

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"

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
	route := c.Path()
	err_msg := fmt.Sprintf("%s: %s", msg, err.Error())
	log.Printf("%s [%s] %s", server_prefix, route, err_msg)
	return c.String(status, err_msg)
}

func getVideoMediaDir(media_dir string, video_hash string) string {
	return media_dir + "/0x" + video_hash
}


// execPythonSubprocess will find local python interpreter and execute commands using it
func execPythonSubprocess(args ...string) (float64, error) {
	var python_exec = getLocalPythonInterpreter()
	var start = time.Now()
	cmd := exec.Command( python_exec, args... )
	if output, err := cmd.CombinedOutput(); err != nil {
		log.Printf("STDOUT\n****\n%s\n****", string(output))
		return -1, err
	}
	return time.Since(start).Seconds(), nil
}


// execPythonSubprocess will find local python interpreter and execute commands using it
func execPythonSubprocess_Output[R any](args ...string) (R, error) {
	var reply R
	
	var python_exec = getLocalPythonInterpreter()
	cmd := exec.Command( python_exec, args... )
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("STDOUT\n****\n%s\n****", string(output))
		return reply, err
	}
	// unmarshal
	if err := json.Unmarshal(output, &reply); err != nil {
		return reply, err
	}
	return reply, nil
}


func getLocalPythonInterpreter() string {
    var path string
    if runtime.GOOS == "windows" {
        path = ".venv\\Scripts\\python.exe"
    } else {
        path = ".venv/bin/python3"
    }

	if _, err := os.Stat(path); err == nil {
		return path
	}

    log.Fatal("No local Python interpreter found in .venv")
    return "" // unreachable, but required
}


func getPreviewThumbnail(vid_media_dir string, large_thumbs bool) (string, error) {

	// if prevthumb not exist
	var prev_thumbs_dir = vid_media_dir + "/previewthumbs"
	entries, err := os.ReadDir(prev_thumbs_dir)
	if err != nil || len(entries) < 10 {
		return "NONE HAHAHA", err
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
