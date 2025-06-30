""" Routes for api/media/ (eg. get-poster/) which handle checking that media exists and their creation """
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import FileResponse
import os

from handymatt.wsl_paths import convert_to_wsl_path
from handymatt_media import media_generator

from .. import db
from config import PREVIEW_MEDIA_DIR, CUSTOM_THUMBS_DIR
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
        raise HTTPException(404, 'No data found for that hash')
    video_path = convert_to_wsl_path(video_data.path)
    if not os.path.exists(video_path):
        raise HTTPException(404, 'Video path doesnt exist')
    return FileResponse(video_path, media_type='video/mp4')


# ENSURE SEEK THUMBNAIL (Gets Poster)
@media_router.get("/get/poster/{video_hash}")
def confirm_poster(video_hash: str):
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        print("Could not find video with hash:", video_hash)
        return Response("No video with that hash", 404)
    thumbnail = checkers.hasPreviewThumbs(video_hash, PREVIEW_MEDIA_DIR, small=False)
    if thumbnail is None:
        thumbnail = checkers.hasPoster(video_hash, PREVIEW_MEDIA_DIR) # use simpler poster
        if thumbnail is None:
            print("Generating placeholder poster for:", video_data.filename)
            try:
                thumbnail = generators.generatePosterSimple(video_data.path, video_hash, PREVIEW_MEDIA_DIR, video_data.duration_seconds)
            except FileNotFoundError as e:
                print('ERROR: Cant generate poster, video not found:', video_data.path)
            if thumbnail is None:
                return Response("Failed to generate poster", 500)
    thumbnail_path = f'{PREVIEW_MEDIA_DIR}/0x{video_hash}/{thumbnail}'
    if not os.path.exists(thumbnail_path):
        return Response('Thumbnail doesnt exist', 500)
    return FileResponse(thumbnail_path)


# ENSURE PREVIEW THUMBNAILS
@media_router.get("/ensure/preview-thumbnails/{video_hash}")
def confirm_preview_thumbnails(video_hash: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    return jsonify(generateReponse("Not implemented")), 404
    r = videos_dict.get(hash)
    if not r:
        print("Could not find video with hash:", hash)
        return jsonify("No video with that hash"), 404
    if not bf.media_hasPoster(hash, MEDIADIR):
        print("Generating early poster for:", r['filename'])
        ret = bf.media_generatePosterSimple(r['path'], hash, MEDIADIR, r['duration_seconds'])
        if not ret:
            return jsonify(generateReponse("Failed to generate poster")), 400
    return jsonify(generateReponse()), 200


# ENSURE SEEK THUMBNAIL
@media_router.get("/ensure/teaser-small/{video_hash}")
def confirm_teaser_small(video_hash: str):
    # return Response('Temporarily disabled', 503)
    print("[TEASER] Confirming small teaser for hash: ", video_hash)
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        raise HTTPException(404, f'Could not find video with hash: {video_hash}')
    if not checkers.hasTeaserSmall(video_hash, PREVIEW_MEDIA_DIR):
        teaser = "NULL_PATH"
        try:
            teaser = generators.generateTeaserSmall(video_data.path, video_hash, PREVIEW_MEDIA_DIR, video_data.duration_seconds)
        except FileNotFoundError as e:
            print('ERROR: Cant generate teaser, video not found:', video_data.path)
        if not os.path.exists(teaser):
            raise HTTPException(500, 'Small teaser generation failed')
    return {'msg': 'good!'}


# ENSURE SEEK THUMBNAIL
@media_router.get("/ensure/teaser-large/{video_hash}")
def confirm_teaser_large(video_hash: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    print("[TEASER] Confirming large teaser for hash: ", hash)
    r = videos_dict.get(hash)
    if r == None:
        print("Could not find video with hash:", hash)
        return jsonify(), 404
    if not bf.media_hasTeaserLarge(hash, MEDIADIR):
        print("[TEASER] Generating large teaser")
        teaser_path = bf.media_generateTeaserLarge(r['path'], hash, MEDIADIR, r['duration_seconds'])
        if not os.path.exists(teaser_path):
            print("[TEASER] ERROR: Generating teaser FAILED!")
            return jsonify(), 400
        return jsonify(generateReponse('Large teaser generated!')), 200
    return jsonify(generateReponse('Large teaser already exists')), 200


# ENSURE SEEK THUMBNAIL
@media_router.get("/ensure/seek-thumbnails/{video_hash}")
def confirm_seek_thumbnails(video_hash: str):
    # return Response('Temporarily disabled', 503)

    # check they exist
    vid_media_dir = generators.get_video_media_dir(PREVIEW_MEDIA_DIR, video_hash)
    if os.path.exists( vid_media_dir + '/seekthumbs.jpg') and os.path.exists( vid_media_dir + '/seekthumbs.vtt' ):
        return {'msg': 'Video has seek thumbs!'}
        return Response('Video has seek thumbnails', 200)
    
    # get video data
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        return Response('No video with that hash', 404)

    # 
    print(f'Generating seek thumbnails for : "{video_data.path}"')
    try:
        _ = media_generator.generateSeekThumbnails(video_data.path, vid_media_dir, n=400)
    except Exception as e:
        print('ERROR: Unable to generate seek thumbnails:\n', e)
        return Response('Unable to generate seek thumbs for video', 500)
    
    if os.path.exists( vid_media_dir + '/seekthumbs.jpg') and os.path.exists( vid_media_dir + '/seekthumbs.vtt' ):
        return {'msg': 'Video has seek thumbs!'}
        return Response(f'Video has seekthumbs', 200)

    return Response('Unable to generate seek thumbs for video', 500)


# ENSURE SEEK THUMBNAIL
@media_router.get("/get/subtitles/{video_hash}")
def ROUTER_get_subtitles(video_hash: str):
    return FileResponse(r'A:\Whispera\videos\JAV\.subtitles\JUL-617.srt')
