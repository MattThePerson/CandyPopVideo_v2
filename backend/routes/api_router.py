import random
import time
from fastapi import APIRouter, Response, Depends, HTTPException

from handymatt.wsl_paths import convert_to_wsl_path, convert_to_windows_path

from ..util import media
from ..objects.app_state import AppState

_media_dir = convert_to_wsl_path(r'A:\WhisperaHQ\MyPrograms\MyApplications\CandyPopApp\Frontend\media\videos')


def generateReponse(main=None, time_taken=None):
    r = {}
    r['collections'] = ['main'] # state.metadataHandler.getValue('collections', [])
    r['main'] = main
    r['time_taken'] = time_taken
    return r


state = AppState()
api_router = APIRouter()

# test
@api_router.get("/hello")
def read_root():
    return {"message": "Hello there!"}


# GET VIDEO
@api_router.get("/get-video-data/{video_hash}")
def get_video(video_hash: str):
    print("Request recieved: 'get-video', hash: ", video_hash)
    video_data = state.videos_dict.get(video_hash)
    if not video_data:
        print("Could not find video with hash:", video_hash)
        return Response(status_code=404, content=f"No video with hash: {video_hash}")
    print("Found video:", video_data.path)
    if not media.hasPoster(video_hash, _media_dir):
        print("Generating early poster for:", video_data.filename)
        media.generatePosterSimple(video_data.path, video_hash, _media_dir, video_data.duration_seconds)
    # r['is_favourite'] = bf.is_favourite(video_hash, state.metadataHandler)
    poster = media.hasPreviewThumbs(video_hash, _media_dir, small=True)
    if poster == None:
        poster = media.hasPoster(video_hash, _media_dir)
    response = video_data.to_dict()
    response['poster'] = poster
    # update views
    if state.videosHandler:
        videodata = state.videosHandler.getValue(video_hash)
        videodata['views'] = videodata.get('views', 0) + 1
        state.videosHandler.setValue(video_hash, response)
    # Add viewing to metadata
    view_item = {'ts': time.time(), 'hash': video_hash}
    if state.metadataHandler:
        state.metadataHandler.appendValue('view_history', view_item)
    return generateReponse(response)


# GET RANDOM VIDEO
@api_router.get("/get-random-video")
def get_random_video():
    print("Request recieved: 'get-random-video'")
    #r = random.choice([1234, 2134, 3322, 4321, "fe21acc7"])
    
    hashes = list(state.videos_dict.keys())
    r = random.choice(hashes)
    print('random:', r)
    response = {'hash' : r}
    if not response:
        return generateReponse('Nothing!')
    return {'main': response}


# GET RANDOM VIDEO
@api_router.get("/get-random-video-seeded/{seed}")
def get_random_video_seeded(seed):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    print("Request recieved: 'get-random-video'")
    print("SEED:", seed)
    rng = random.Random(seed)
    r = rng.choice(list(videos_dict.keys()))
    response = {'hash' : r}
    if not response:
        return jsonify(generateReponse()), 400
    return jsonify(generateReponse(response)), 200


# GET RANDOM SPOTLIGHT VIDEO
@api_router.get("/get-random-spotlight-video")
def get_random_spotlight_video():
    return Response('Not yet implemented', 501)
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    print("Request recieved: 'get-random-video'")
    seed = (datetime.now() - datetime.strptime('1900 06:00:00', '%Y %H:%M:%S')).days
    print("SEED:", seed)
    rng = random.Random(seed)
    r = rng.choice(list(videos_dict.keys()))
    response = {'hash' : r}
    if not response:
        return jsonify(generateReponse()), 400
    return jsonify(generateReponse(response)), 200


# ADD FAVOURITE
@api_router.get("/add-favourite/{video_hash}")
def add_favourite(video_hash: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    if bf.is_favourite(hash, metadataHandler):
        return jsonify('favourite already exists'), 200
    bf.add_favourite(hash, metadataHandler)
    return jsonify('added favourite'), 200


# REMOVE FAVOURITE
@api_router.get("/remove-favourite/{video_hash}")
def remove_favourite(video_hash: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    if not bf.is_favourite(hash, metadataHandler):
        return jsonify('video already not favourites'), 200
    bf.remove_favourite(hash, metadataHandler)
    return jsonify('removed favourite'), 200


# IS FAVOURITE
@api_router.get("/is-favourite/{video_hash}")
def is_favourite(video_hash: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    if bf.is_favourite(hash, metadataHandler):
        return jsonify(generateReponse({'is_favourite': True})), 200
    return jsonify(generateReponse({'is_favourite': False})), 200


# GET ALL PERFORMERS
@api_router.get("/get-performers")
def get_performers():
    return Response('Not yet implemented', 501)
    # return jsonify("Not implemented"), 404
    print(len(state.videos_dict))
    items = ff.getPerformers(state.videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500


# GET ALL STUDIOS
@api_router.get("/get-studios")
def get_studios():
    return Response('Not yet implemented', 501)
    items = ff.getStudios(videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500

# endregion