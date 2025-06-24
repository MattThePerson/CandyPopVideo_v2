""" Routes for api/media/ (eg. get-poster/) which handle checking that media exists and their creation """
from fastapi import APIRouter, Response
import os

from handymatt_media import media_generator

from config import PREVIEW_MEDIA_DIR, CUSTOM_THUMBS_DIR
from ..util import media
from ..schemas import VideoData
from .. import db


ensure_media_router = APIRouter()


# CONFIRM SEEK THUMBNAIL
@ensure_media_router.get("/ensure-media/poster/{video_hash}")
def confirm_poster(video_hash: str):
    return Response('Not implemented', 501)
    video_object = state.videos_dict.get(video_hash)
    if video_object is None:
        print("Could not find video with hash:", video_hash)
        return Response("No video with that hash", 404)
    # poster = media.hasPreviewThumbs(video_hash, PREVIEW_MEDIA_DIR, small=False)
    poster = None
    if poster is None:
        poster = media.hasPoster(video_hash, PREVIEW_MEDIA_DIR) # use simpler poster
        if poster is None:
            print("Generating placeholder poster for:", video_object.filename)
            poster = media.generatePosterSimple(video_object.path, video_hash, PREVIEW_MEDIA_DIR, video_object.duration_seconds)
            if poster is None:
                return Response("Failed to generate poster", 500)
    custom_thumb = media.hasCustomThumb(video_hash, CUSTOM_THUMBS_DIR)
    return_obj = { 'poster_rel_path': poster, 'custom_thumb': custom_thumb }
    return { 'main': return_obj }


# CONFIRM SEEK THUMBNAIL
@ensure_media_router.get("/ensure-media/seek-thumbnails/{video_hash}")
def confirm_seek_thumbnails(video_hash: str):
    return Response('Temporarily disabled', 503)

    # check they exist
    vid_media_dir = media._getMediaDirByHash(video_hash, PREVIEW_MEDIA_DIR)
    if os.path.exists( vid_media_dir + '/seekthumbs.jpg') and os.path.exists( vid_media_dir + '/seekthumbs.vtt' ):
        return Response('Video has seek thumbnails', 200)
    
    # get video data
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if video_data is None:
        return Response('No video with that hash', 404)

    # 
    print(f'Generating seek thumbnails for : "{video_data.path}"')
    try:
        _ = media_generator.generateSeekThumbnails(video_data.path, vid_media_dir)
    except Exception as e:
        print('ERROR: Unable to generate seek thumbnails')
        print(e)
        return Response('Unable to generate seek thumbs for video', 500)
    
    if os.path.exists( vid_media_dir + '/seekthumbs.jpg') and os.path.exists( vid_media_dir + '/seekthumbs.vtt' ):
        return Response(f'Video has seekthumbs', 200)

    return Response('Unable to generate seek thumbs for video', 500)


# CONFIRM PREVIEW THUMBNAILS
@ensure_media_router.get("/ensure-media/preview-thumbnails/{video_hash}")
def confirm_preview_thumbnails(video_hash: str):
    return Response('Not implemented', 501)
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


# CONFIRM SEEK THUMBNAIL
@ensure_media_router.get("/ensure-media/teaser-small/{video_hash}")
def confirm_teaser_small(video_hash: str):
    return Response('Not implemented', 501)
    print("[TEASER] Confirming small teaser for hash: ", hash)
    r = videos_dict.get(hash)
    if r == None:
        print("Could not find video with hash:", hash)
        return jsonify(), 404
    if not bf.media_hasTeaserSmall(hash, MEDIADIR):
        print("[TEASER] Generating small teaser")
        teaser_path = bf.media_generateTeaserSmall(r['path'], hash, MEDIADIR, r['duration_seconds'])
        if not os.path.exists(teaser_path):
            print("[TEASER] ERROR: Generating teaser FAILED!")
            return jsonify(), 400
        return jsonify(generateReponse('Small teaser generated!')), 200
    return jsonify(generateReponse('Small teaser already exists')), 200


# CONFIRM SEEK THUMBNAIL
@ensure_media_router.get("/ensure-media/teaser-large/{video_hash}")
def confirm_teaser_large(video_hash: str):
    return Response('Not implemented', 501)
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
