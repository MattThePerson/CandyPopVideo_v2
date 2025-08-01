package routes

import (
	"cpv_backend/internal/db"
	"cpv_backend/internal/schemas"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/labstack/echo/v4"
)


func IncludeMediaRoutes(e *echo.Group, db_path string, preview_media_dir string, subtitle_folders []string) {


	// #region - GET VIDEO -----------------------------------------------------
	e.GET("/get/video/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 500, "Unable to get data for hash: "+video_hash, err)
		}
		return c.File(vd.Path)
	})


	// #region - GET POSTER ---------------------------------------------------------
	e.GET("/get/poster/:video_hash", func(c echo.Context) error {
		var video_hash = c.Param("video_hash")
		var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)

		// check for preview thumbs
		preview_thumb, err := getPreviewThumbnail(vid_media_dir, false)
		if err == nil {
			// fmt.Println("FOUND PREVIEW THUMB: "+preview_thumb)
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
		fmt.Println("[subprocess] creating `Simple Poster` for: "+video_hash+" ...")
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
		
		return c.String(500, "Unable to create `Simple Poster` for hash: "+video_hash)
	})


	// #region - VID TEASER (s) --------------------------------------------------
	e.GET("/ensure/teaser-small/:video_hash", func(c echo.Context) error {
		var video_hash = c.Param("video_hash")
		var vid_media_dir = getVideoMediaDir(preview_media_dir, video_hash)
		var media_stem = "teaser_small.mp4"
		var media_path = vid_media_dir + "/" + media_stem
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		
		// get video data
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 404, "No video data for hash: "+video_hash, err)
		}

		// [subprocess] create media with subprocess
		fmt.Printf("[EXEC] Generating 'Video Teaser (small)' for: `%s` ...\n", video_hash)
		tt, err := execPythonSubprocess(
			"python_src/worker_scripts/generateVideoTeaser.py",
			"-path", vd.Path,
			"-mediadir", vid_media_dir,
			"-duration_sec", fmt.Sprintf("%.1f", vd.DurationSeconds),
			"-filestem", media_stem,
			"-type", "small",
		)
		if err != nil {
			handleServerError(c, 500, "Unable to ", err)
		}
		fmt.Printf("[EXEC] Done. 'Video Teaser (small)' generated in %.1f seconds\n", tt)

		// check media exists
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		return c.String(500, "Unable to create `Video Teaser (small)` for hash: "+video_hash)
	})


	// #region - TEASER THUMBS (S) ------------------------------------------
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
		fmt.Printf("[EXEC] Generating 'Teaser Thumbs (small)' for: `%s` ...\n", video_hash)
		tt, err := execPythonSubprocess(
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
		fmt.Printf("[EXEC] Done. 'Teaser Thumbs (small)' generated in %.1f seconds\n", tt)

		// check media exists
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		return c.String(500, "Unable to create `Teaser Thumbs (small)` for hash: "+video_hash)
	})


	// #region - SEEK THUMBS --------------------------------------------------
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
		fmt.Printf("[EXEC] Generating 'Seek Thumbs' for: `%s` ...\n", video_hash)
		tt, err := execPythonSubprocess(
			"python_src/worker_scripts/generateVideoSpritesheet.py",
			"-path", vd.Path,
			"-mediadir", vid_media_dir,
			"-num", "400",
			"-height", "300",
			"-filestem", "seekthumbs",
		)
		if err != nil {
			handleServerError(c, 500, "Unable to generate seek thumbs with subprocess", err)
		}
		fmt.Printf("[EXEC] Done. 'Seek Thumbs' generated in %.1f seconds\n", tt)

		// check media exists
		if _, err := os.Stat(media_path); err == nil {
			return c.String(200, "media exists")
		}
		return c.String(500, "Unable to create `Seek Thumbs` for hash: "+video_hash)
	})


	// #region - GET SUBS --------------------------------------------------
	e.GET("/get/subtitles/:video_hash", func(c echo.Context) error {
		video_hash := c.Param("video_hash")
		check := c.QueryParam("check") == "true" 
		vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", video_hash)
		if err != nil {
			handleServerError(c, 500, "Unable to get data for hash: "+video_hash, err)
		}

		// get id to use
		var filebase = filepath.Base(vd.Path)
		id := ""
		if vd.DVDCode != nil {
			id = *vd.DVDCode
		} else if vd.SourceID != nil {
			id = *vd.SourceID
		} else {
			id = strings.TrimSuffix(filebase, filepath.Ext(vd.Path))
		}
		
		// construct subtitle folder list
		var check_folders = []string{
			filebase,
			filepath.Join(filebase, ".subtitles"),
		}
		check_folders = append(check_folders, subtitle_folders...)

		// check folders
		for _, f := range check_folders {
			pth := fmt.Sprintf("%s/%s.srt", f, id)
			if _, err := os.Stat(pth); err == nil {
				if check {
					return c.String(200, "All good bro")
				}
				return c.File(pth)
			}
		}
		
		return c.NoContent(204)
	})


	// // #region - GET POSTER LARGE --------------------------------------------------
	// e.GET("/get/poster-large/:video_hash", func(c echo.Context) error {
	// 	video_hash := c.Param("video_hash")
	// 	return c.String(501, "Not implemented: "+video_hash)
	// })


	// // #region - ENSURE TEASER LARGE --------------------------------------------------
	// e.GET("/ensure/teaser-large/:video_hash", func(c echo.Context) error {
	// 	video_hash := c.Param("video_hash")
	// 	return c.String(501, "Not implemented: "+video_hash)
	// })


	// // #region - ENSURE TEASER THUMBS (large) --------------------------------------------------
	// e.GET("/ensure/teaser-thumbs-large/:video_hash", func(c echo.Context) error {
	// 	video_hash := c.Param("video_hash")
	// 	return c.String(501, "Not implemented: "+video_hash)
	// })

}
