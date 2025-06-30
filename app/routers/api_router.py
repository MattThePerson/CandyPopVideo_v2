import random
import time
from datetime import datetime
from fastapi import APIRouter, Response, Depends, HTTPException

from handymatt.wsl_paths import convert_to_wsl_path, convert_to_windows_path

from ..schemas import VideoData
from ..media import generators
from .. import db



api_router = APIRouter()


# GET VIDEO
@api_router.get("/get/video-data/{video_hash}")
def ROUTE_get_video(video_hash: str):
    print("Request recieved: 'get-video', hash: ", video_hash)
    video_dict = db.read_object_from_db(video_hash, 'videos')
    if video_dict is None:
        print("Could not find video with hash:", video_hash)
        return Response(f"No video with that hash", 404)
    video_data = VideoData.from_dict( video_dict )
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
@api_router.get("/get/random-video-hash-seeded/{seed}")
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
@api_router.get("/get/random-spotlight-video-hash")
def ROUTE_get_random_spotlight_video():
    seed = (datetime.now() - datetime.strptime('1900 06:00:00', '%Y %H:%M:%S')).days
    rng = random.Random(seed)
    videos_dict = db.read_table_as_dict('videos')
    video_hashes = sorted([ hsh for hsh, vd in videos_dict.items() if vd.get('is_linked') ])
    if video_hashes == []:
        print('No videos loaded')
        raise HTTPException(status_code=404, detail="No videos found")
    random_hash = rng.choice( video_hashes )
    return { 'hash' : random_hash }


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


