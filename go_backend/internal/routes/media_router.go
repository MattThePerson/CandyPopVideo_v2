package routes

import (
	"cpv_backend/internal/db"
	"cpv_backend/internal/schemas"
	"fmt"
	"os"
	"os/exec"
	"strconv"

	"github.com/labstack/echo/v4"
)


func IncludeMediaRoutes(e *echo.Group, db_path string, preview_media_dir string) {


	/* - GET VIDEO ---------------------------------------------------------- */
	e.GET("/get/video/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 500, "Unable to get data for hash: "+video_hash, err)
		}
		return c.File(vd.Path)
	})


	/* - GET POSTER --------------------------------------------------------- */
	e.GET("/get/poster/:video_hash", func(c echo.Context) error {
		var video_hash = c.Param("video_hash")
		var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)

		// check for preview thumbs
		preview_thumb, err := getPreviewThumbnail(vid_media_dir, false)
		if err == nil {
			return c.File(preview_thumb)
		}

		// check for poster
		var poster_pth = vid_media_dir + "/poster.png"
		if _, err := os.Stat(poster_pth); err == nil {
			return c.File(poster_pth)
		}

		// get video data
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 404, "No video data for hash: "+video_hash, err)
		}

		// [subprocess] video poster
		fmt.Println("[subprocess] creating simple poster")
		os.MkdirAll(vid_media_dir, 0755)
		cmd := exec.Command(
			"ffmpeg",
			"-ss", strconv.Itoa(int( vd.DurationSeconds*0.2 )),
			"-i", vd.Path,
			"-frames:v", "1",
			poster_pth,
			"-loglevel", "quiet",
		)
		if _, err := cmd.CombinedOutput(); err != nil {
			handleServerError(c, 500, "Unable to generate simple poster", err)
		}

		// check media exists
		if _, err := os.Stat(poster_pth); err == nil {
			return c.File(poster_pth)
		}
		
		return c.String(500, "unable to ensure poster for video")
	})


	/* - _ -------------------------------------------------- */
	e.GET("/ensure/teaser-small/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})


	/* - ENSURE TEASER THUMBS (small) ------------------------------------------ */
	e.GET("/ensure/teaser-thumbs-small/:video_hash", func(c echo.Context) error {
		var video_hash = c.Param("video_hash")
		var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
		var media_path = vid_media_dir + "/teaser_thumbs_small.jpg"
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		
		// get video data
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 404, "No video data for hash: "+video_hash, err)
		}

		// [subprocess] create media with subprocess
		fmt.Println("Ensuring teaser thumbs (small) for: "+video_hash)
		output, err := execPythonSubprocess(
			"python_src/worker_scripts/generateVideoSpritesheet.py",
			"-path", vd.Path,
			"-mediadir", vid_media_dir,
			"-num", "16",
			"-height", "300",
			"-filestem", "teaser_thumbs_small",
		)
		if err != nil {
			handleServerError(c, 500, "Unable to ", err)
		}
		fmt.Println("SUBPROCESS OUTPUT: "+string(output));

		// check media exists
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		return c.String(500, "Unable to create `teaser_thumbs_small` for hash: "+video_hash)
	})


	/* - ENSURE SEEK THUMBS -------------------------------------------------- */
	e.GET("/ensure/seek-thumbnails/:video_hash", func(c echo.Context) error {
		var video_hash = c.Param("video_hash")
		var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
		var media_path = vid_media_dir + "/seekthumbs.jpg"
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		
		// get video data
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 404, "No video data for hash: "+video_hash, err)
		}

		// [subprocess] create media with subprocess
		fmt.Println("Ensuring seekthumbs for: "+video_hash)
		output, err := execPythonSubprocess(
			"python_src/worker_scripts/generateVideoSpritesheet.py",
			"-path", vd.Path,
			"-mediadir", vid_media_dir,
			"-num", "400",
			"-height", "300",
			"-filestem", "seekthumbs",
		)
		if err != nil {
			handleServerError(c, 500, "Unable to generate seek thumbs", err)
		}
		fmt.Println("SUBPROCESS OUTPUT: "+string(output));

		// check media exists
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		return c.String(200, "Hopefully exists idk")
	})


	/* - _ -------------------------------------------------- */
	e.GET("/get/subtitles/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		return c.String(501, "Not implemented: "+video_hash)
	})


	// /* - GET POSTER LARGE -------------------------------------------------- */
	// e.GET("/get/poster-large/:video_hash", func(c echo.Context) error {
	// 	video_hash := c.Param("video_hash")
	// 	return c.String(501, "Not implemented: "+video_hash)
	// })


	// /* - ENSURE TEASER LARGE -------------------------------------------------- */
	// e.GET("/ensure/teaser-large/:video_hash", func(c echo.Context) error {
	// 	video_hash := c.Param("video_hash")
	// 	return c.String(501, "Not implemented: "+video_hash)
	// })


	// /* - ENSURE TEASER THUBS (large) -------------------------------------------------- */
	// e.GET("/ensure/teaser-thumbs-large/:video_hash", func(c echo.Context) error {
	// 	video_hash := c.Param("video_hash")
	// 	return c.String(501, "Not implemented: "+video_hash)
	// })

}
