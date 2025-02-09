""" Routes for api/media/ (eg. get-poster/) which handle checking that media exists and their creation """
from fastapi import APIRouter, Response

from ..util import media
from ..objects.app_state import AppState
from config import PREVIEW_MEDIA_DIR, CUSTOM_THUMBS_DIR

# _media_dir, _custom_thumbs_dir = '', ''

state = AppState()
api_media_router = APIRouter()


# CONFIRM SEEK THUMBNAIL
@api_media_router.get("/get-poster/{video_hash}")
def confirm_poster(video_hash: str):
    # return Response('Not yet implemented', 501)
    video_object = state.videos_dict.get(video_hash)
    if video_object is None:
        print("Could not find video with hash:", video_hash)
        return Response("No video with that hash", 404)
    # poster = media.hasPreviewThumbs(video_hash, PREVIEW_MEDIA_DIR, small=False)
    poster = None
    if poster is None:
        poster = media.hasPoster(video_hash, PREVIEW_MEDIA_DIR) # use simpler poster
        if poster is None:
            print("Generating placeholder poster for:", video_object['filename'])
            poster = media.generatePosterSimple(video_object['path'], video_hash, PREVIEW_MEDIA_DIR, video_object['duration_seconds'])
            if poster is None:
                return Response("Failed to generate poster", 500)
    custom_thumb = media.hasCustomThumb(video_hash, CUSTOM_THUMBS_DIR)
    return_obj = { 'poster_rel_path': poster, 'custom_thumb': custom_thumb }
    return { 'main': return_obj }


# CONFIRM SEEK THUMBNAIL
@api_media_router.get("/get-seek-thumbnails/{video_hash}")
def confirm_seek_thumbnails(video_hash: str):
    return Response('Not yet implemented', 501)
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    global generate_thumbnails_thread
    r = videos_dict.get(hash)
    if not r:
        print("Could not find video with hash:", hash)
        return jsonify(), 404
    if not bf.media_hasSeekThumbs(hash, MEDIADIR, r['duration_seconds']):
        print("WANNA MAKE SEEK THUMBS FOR: ", r['filename'])
        if generate_thumbnails_thread and generate_thumbnails_thread.is_alive():
            return jsonify("Thread busy"), 400
        print("[THREAD] Starting generate thumbnails thread ...")
        generate_thumbnails_thread = threading.Thread(target=bf.media_generateSeekThumbs, args=(r['path'], hash, MEDIADIR, r['duration_seconds']))
        generate_thumbnails_thread.start()
        generate_thumbnails_thread.join()
        print("[GENERATE] Seek thumbnails generated!")
        return jsonify("Seek thumbnails generated!"), 200
    return jsonify("Seek thumbnails already exist!"), 200


# CONFIRM PREVIEW THUMBNAILS
@api_media_router.get("/get-preview-thumbnails/{video_hash}")
def confirm_preview_thumbnails(video_hash: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
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
@api_media_router.get("/get-teaser-small/{video_hash}")
def confirm_teaser_small(video_hash: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
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
@api_media_router.get("/get-teaser-large/{video_hash}")
def confirm_teaser_large(video_hash: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
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
