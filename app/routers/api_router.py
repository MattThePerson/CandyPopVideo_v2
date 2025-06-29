import random
import time
from fastapi import APIRouter, Response, Depends, HTTPException

from handymatt.wsl_paths import convert_to_wsl_path, convert_to_windows_path

from ..schemas import VideoData
from ..media import generators
from .. import db


def generateReponse(main=None, time_taken=None):
    r = {}
    r['collections'] = ['main'] # state.metadataHandler.getValue('collections', [])
    r['main'] = main
    r['time_taken'] = time_taken
    return r


api_router = APIRouter()


# GET VIDEO
@api_router.get("/get/video-data/{video_hash}")
def ROUTE_get_video(video_hash: str):
    print("Request recieved: 'get-video', hash: ", video_hash)
    video_data = VideoData.from_dict( db.read_object_from_db(video_hash, 'videos') )
    if not video_data:
        print("Could not find video with hash:", video_hash)
        return Response(f"No video with that hash", 404)
    print("Found video:", video_data.path)
    response = video_data.to_dict()
    return response
    # update views
    # if state.videosHandler:
    #     videodata = state.videosHandler.getValue(video_hash)
    #     videodata['views'] = videodata.get('views', 0) + 1
    #     state.videosHandler.setValue(video_hash, response)
    # Add viewing to metadata
    view_item = {'ts': time.time(), 'hash': video_hash}
    # if state.metadataHandler:
    #     state.metadataHandler.appendValue('view_history', view_item)
    return generateReponse(response)

# get("/get/video-metadata/{video_hash}")


# GET RANDOM VIDEO
@api_router.get("/get/random-video-hash")
def ROUTE_get_random_video():
    video_dicts = db.read_table_as_dict('videos')
    if video_dicts == {}:
        raise HTTPException(status_code=404, detail='Not implemented')
    rando_hash = random.choice([ hsh for hsh, dct in video_dicts.items() if dct.get('is_linked') ])
    print('random hash:', rando_hash)
    return {'hash' : rando_hash}


# GET RANDOM VIDEO
@api_router.get("/get/random-video-seeded/{seed}")
def ROUTE_get_random_video_seeded(seed):
    raise HTTPException(status_code=501, detail='Not implemented')
    print("Request recieved: 'get-random-video'")
    print("SEED:", seed)
    rng = random.Random(seed)
    r = rng.choice(list(videos_dict.keys()))
    response = {'hash' : r}
    if not response:
        return jsonify(generateReponse()), 400
    return jsonify(generateReponse(response)), 200


# GET RANDOM SPOTLIGHT VIDEO
@api_router.get("/get/random-spotlight-video")
def ROUTE_get_random_spotlight_video():
    raise HTTPException(status_code=501, detail='Not implemented')
    print("Request recieved: 'get-random-video'")
    seed = (datetime.now() - datetime.strptime('1900 06:00:00', '%Y %H:%M:%S')).days
    print("SEED:", seed)
    rng = random.Random(seed)
    r = rng.choice(list(videos_dict.keys()))
    response = {'hash' : r}
    if not response:
        return jsonify(generateReponse()), 400
    return jsonify(generateReponse(response)), 200


# GET ALL PERFORMERS
@api_router.get("/get/all-performers")
def ROUTE_get_performers():
    raise HTTPException(status_code=501, detail='Not implemented')
    print(len(state.videos_dict))
    items = ff.getPerformers(state.videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500


# GET ALL STUDIOS
@api_router.get("/get/all-studios")
def ROUTE_get_studios():
    raise HTTPException(status_code=501, detail='Not implemented')
    items = ff.getStudios(videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500


# GET CATALOGURE
@api_router.get("/get/catalogue")
def ROUTE_get_catalogue():
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    raise HTTPException(status_code=501, detail='Not implemented')
    items = ff.getStudios(videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500


# ADD FAVOURITE
@api_router.post("/favourites/add/{video_hash}")
def ROUTE_add_favourite(video_hash: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    if bf.is_favourite(hash, metadataHandler):
        return jsonify('favourite already exists'), 200
    bf.add_favourite(hash, metadataHandler)
    return jsonify('added favourite'), 200


# REMOVE FAVOURITE
@api_router.post("/favourites/remove/{video_hash}")
def ROUTE_remove_favourite(video_hash: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    if not bf.is_favourite(hash, metadataHandler):
        return jsonify('video already not favourites'), 200
    bf.remove_favourite(hash, metadataHandler)
    return jsonify('removed favourite'), 200


# IS FAVOURITE
@api_router.get("/favourites/is-fav/{video_hash}")
def ROUTE_is_favourite(video_hash: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    if bf.is_favourite(hash, metadataHandler):
        return jsonify(generateReponse({'is_favourite': True})), 200
    return jsonify(generateReponse({'is_favourite': False})), 200


# post("/views/add/{video_hash}")
# get("/views/get/{video_hash}")

# post("/likes/{video_hash}/add")
# get("/likes/{video_hash}/get")

# get("/rating/{video_hash}/add")
# get("/rating/{video_hash}/get")
