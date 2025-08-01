package routes

import (
	"errors"
	"fmt"
	"log"
	"os"
	"os/exec"
	"runtime"

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

func getVideoMediaDir(media_dir string, video_hash string) string {
	return media_dir + "/0x" + video_hash
}


// execPythonSubprocess will find local python interpreter and execute commands using it
func execPythonSubprocess(args ...string) ([]byte, error) {
	var python_exec = getLocalPythonInterpreter()
	cmd := exec.Command( python_exec, args... )
	return cmd.CombinedOutput();
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

/* GET PREVIEW THUMBS */

func getPreviewThumbnail(vid_media_dir string, large_thumbs bool) (string, error) {

	// if prevthumb not exist
	var prev_thumbs_dir = vid_media_dir + "/preveiwthumbs"
	if _, err := os.Stat(prev_thumbs_dir); errors.Is(err, os.ErrNotExist) {
		return "", errors.New("no preview thumbs")
	}
	
	// get seeded random file
	var res = "360"
	if large_thumbs {
		res = "1080"
	}
	fmt.Println(res);
	return "", nil

}
// vid_folder = f'{get_video_media_dir(mediadir, video_hash)}/previewthumbs'
// if not os.path.exists(vid_folder):
//     return None
// res = '1080' if large else '360'
// thumb_paths = [ os.path.join('previewthumbs', f) for f in os.listdir(vid_folder) if res in f ]
// if thumb_paths == []:
//     return None
// # return thumbnail by second
// delta = (datetime.now() - datetime.strptime('1900', '%Y'))
// i = int(delta.seconds%len(thumb_paths))
// return thumb_paths[i]



