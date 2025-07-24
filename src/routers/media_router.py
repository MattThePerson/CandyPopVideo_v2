""" Routes for media/ (eg. get-poster/) which handle checking that media exists and their creation """
import os
import subprocess
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

# from handymatt_media import media_generator

from src import db
from src.config import PREVIEW_MEDIA_DIR, SUBTITLE_FOLDERS
from ..schemas import VideoData
from ..media import generators, checkers


media_router = APIRouter()

#   ROUTES:
# media/static/<PTH>            -> StaticResponse()
# media/get/<TYPE>/<HSH>        -> FileResponse(): can prompt creation  TYPE=[video, poster, ...]
# media/ensure/<TYPE>/<HSH>     -> Response(): ensures media exists, prompts creation


# videos route
@media_router.get('/get/video/{video_hash}')
def xyz(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        raise HTTPException(status_code=404, detail="No data found for that hash")
    video_path = video_data.path
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video path doesn't exist")
    return FileResponse(video_path, media_type='video/mp4')


# 
@media_router.get("/get/poster/{video_hash}")
def ROUTER_get_poster(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        print("Could not find video with hash:", video_hash)
        raise HTTPException(status_code=404, detail="No video with that hash")
    thumbnail = checkers.hasPreviewThumbs(video_hash, PREVIEW_MEDIA_DIR, large=False)
    if thumbnail is None:
        thumbnail = checkers.hasPoster(video_hash, PREVIEW_MEDIA_DIR) # use simpler poster
        if thumbnail is None:
            print("Generating placeholder poster for:", video_data.filename)
            try:
                thumbnail = generators.generatePosterSimple(video_data.path, video_hash, PREVIEW_MEDIA_DIR, video_data.duration_seconds)
            except FileNotFoundError as e:
                print('ERROR: Cant generate poster, video not found:', video_data.path)
            if thumbnail is None:
                raise HTTPException(status_code=500, detail="Failed to generate poster")
    thumbnail_path = f'{PREVIEW_MEDIA_DIR}/0x{video_hash}/{thumbnail}'
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=500, detail="Thumbnail doesn't exist")
    return FileResponse(thumbnail_path)


# UNUSED
@media_router.get("/get/poster-large/{video_hash}")
def ROUTER_get_poster_large(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        print("Could not find video with hash:", video_hash)
        return Response("No video with that hash", 404)
    thumbnail = checkers.hasPreviewThumbs(video_hash, PREVIEW_MEDIA_DIR, large=True)
    if thumbnail is None:
        raise HTTPException(status_code=503, detail='Temporarily disabled')
        try:
            _ = generators.generatePreviewThumbs(video_data.path, video_hash, PREVIEW_MEDIA_DIR, amount=5, n_frames=30*10)
        except FileNotFoundError as e:
            print('ERROR: Cant generate poster, video not found:', video_data.path)
        if not checkers.hasPreviewThumbs(video_hash, PREVIEW_MEDIA_DIR, large=True):
            return Response("Failed to generate poster", 500)
    thumbnail_path = f'{PREVIEW_MEDIA_DIR}/0x{video_hash}/{thumbnail}'
    if not os.path.exists(thumbnail_path):
        return Response('Thumbnail doesnt exist', 500)
    return FileResponse(thumbnail_path)



# 
@media_router.get("/ensure/teaser-small/{video_hash}")
def confirm_teaser_small(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        raise HTTPException(404, f'Could not find video with hash: {video_hash}')
    if not checkers.hasTeaserSmall(video_hash, PREVIEW_MEDIA_DIR):
        # raise HTTPException(status_code=503, detail='Temporarily disabled')
        teaser = "NULL_PATH"
        try:
            teaser = generators.generateTeaserSmall(
                video_data.path,
                video_hash,
                PREVIEW_MEDIA_DIR,
                video_data.duration_seconds,
            )
        except FileNotFoundError as e:
            print('ERROR: Cant generate teaser, video not found:', video_data.path)
        if not os.path.exists(teaser):
            raise HTTPException(500, 'Small teaser generation failed')
    return {'msg': 'good!'}


# UNUSED
@media_router.get("/ensure/teaser-large/{video_hash}")
def confirm_teaser_large(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        raise HTTPException(404, f'Could not find video with hash: {video_hash}')
    if not checkers.hasTeaserLarge(video_hash, PREVIEW_MEDIA_DIR):
        raise HTTPException(status_code=503, detail='Temporarily disabled')
        teaser = "NULL_PATH"
        try:
            teaser = generators.generateTeaserLarge(video_data.path, video_hash, PREVIEW_MEDIA_DIR, video_data.duration_seconds)
        except FileNotFoundError as e:
            print('ERROR: Cant generate teaser, video not found:', video_data.path)
        if not os.path.exists(teaser):
            raise HTTPException(500, 'Large teaser generation failed')
    return {'msg': 'good!'}


# 
@media_router.get("/ensure/seek-thumbnails/{video_hash}")
def confirm_seek_thumbnails(video_hash: str):
    vid_media_dir = checkers.get_video_media_dir(PREVIEW_MEDIA_DIR, video_hash)
    if not (os.path.exists( vid_media_dir + '/seekthumbs.jpg') and os.path.exists( vid_media_dir + '/seekthumbs.vtt' )):
        
        video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
        if video_data is None:
            return Response('No video with that hash', 404)

        script = 'src/media/scripts/generateVideoSpritesheet.py'
        print('[MEDIA] running subprocess:', script)
        try:
            cmd = [
                './.venv/Scripts/python.exe',
                script,
                '-path', video_data.path,
                '-mediadir', vid_media_dir,
                '-num', '400',
                '-height', '300',
                '-filestem', 'seekthumbs',
            ]
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            msg = f'Subprocess error for [{video_hash}] "{video_data.path}":\n{e.stderr}'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
        except Exception as e:
            msg = f'Some other exception occured [{video_hash}] "{video_data.path}":\n{e}'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
        
        if not (os.path.exists( vid_media_dir + '/seekthumbs.jpg') and os.path.exists( vid_media_dir + '/seekthumbs.vtt' )):
            return Response('Unable to generate seek thumbs for video', 500)
    return {'msg': 'Video has seek thumbs!'}


# 
@media_router.get("/ensure/teaser-thumbs-small/{video_hash}")
def ROUTER_ensure_teaser_thumbs_small(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        return Response('No video with that hash', 404)
    vid_media_dir = checkers.get_video_media_dir(PREVIEW_MEDIA_DIR, video_hash)
    media_path = vid_media_dir + '/teaser_thumbs_small.jpg'
    if not os.path.exists( media_path ):
        script = 'src/media/scripts/generateVideoSpritesheet.py'
        print('[MEDIA] running subprocess:', script)
        try:
            cmd = [
                './.venv/Scripts/python.exe',
                script,
                '-path', video_data.path,
                '-mediadir', vid_media_dir,
                '-num', '16',
                '-height', '300',
                '-filestem', 'teaser_thumbs_small',
            ]
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            msg = f'Subprocess error for [{video_hash}] "{video_data.path}":\n{e.stderr}'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
        except Exception as e:
            msg = f'Some other exception occured [{video_hash}] "{video_data.path}":\n{e}'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
        
        if not os.path.exists( media_path ):
            msg = f'Teaser thumbs dont exist after attempted generation for [{video_hash}] "{video_data.path}"'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
    return {'msg': 'all good brotha'}


# UNUSED
@media_router.get("/ensure/teaser-thumbs-large/{video_hash}")
def ROUTER_ensure_teaser_thumbs_large(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        return Response('No video with that hash', 404)
    vid_media_dir = checkers.get_video_media_dir(PREVIEW_MEDIA_DIR, video_hash)
    media_path = vid_media_dir + '/teaser_thumbs_large.jpg'
    print(media_path)
    if not os.path.exists( media_path ):
        raise HTTPException(status_code=503, detail='Temporarily disabled')
        try:
            _ = media_generator.generateSeekThumbnails( video_data.path, vid_media_dir, n=30, height=900, filename='teaser_thumbs_large' )
        except Exception as e:
            msg = f'Unable to generate teaser thumbs for [{video_hash}] "{video_data.path}"'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
        if not os.path.exists( media_path ):
            msg = f'Teaser thumbs dont exist after attempted generation for [{video_hash}] "{video_data.path}"'
            print(msg)
            raise HTTPException(status_code=500, detail=msg)
    return {'msg': 'all good brotha'}


# 
@media_router.get("/get/subtitles/{video_hash}")
def ROUTER_get_subtitles(video_hash: str, check: bool=False):
    try:
        video_object = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    except Exception as e:
        print("Possibly no db for hash:", video_hash)
        raise HTTPException(status_code=500, detail="Possibly no db entry for that hash")
    id_ = video_object.dvd_code or video_object.source_id or Path(video_object.path).stem
    if id_ is None:
        return Response(status_code=204)
        # raise HTTPException(status_code=404, detail="No usable id for video")
    for base_dir in SUBTITLE_FOLDERS:
        srt_path = base_dir + f'/{id_}.srt'
        if os.path.exists(srt_path):
            if check:
                return {'msg', 'all gucci'}
            else:
                return FileResponse(srt_path)
    return Response(status_code=204)
    # raise HTTPException(status_code=404, detail='No subtitles found')



# 
@media_router.get("/ensure/preview-thumbnails/{video_hash}")
def confirm_preview_thumbnails(video_hash: str):
    raise HTTPException(status_code=501, detail='Not implemented')


