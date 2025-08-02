import random
import os
from datetime import datetime
from fastapi import APIRouter, Response, HTTPException

from python_src.util import db
from python_src.util.general import get_sortable_string_tuple
from python_src.schemas import VideoData
from ..api import actor_api


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
    videos_dict = db.read_table_as_dict('videos')
    video_hashes = sorted([ hsh for hsh, vd in videos_dict.items() if vd.get('is_linked') ])
    if video_hashes == []:
        print('No videos loaded')
        raise HTTPException(status_code=404, detail="No videos found")
    random_hash = _get_random_hash_seeded(video_hashes, seed)
    # rng = random.Random(seed)
    # random_hash = rng.choice( video_hashes )
    return random_hash


# GET ALL PERFORMERS
@api_router.get("/get/all-actors")
def ROUTE_get_actors():
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



# GET CURATED COLLECTIONS
@api_router.get("/get/curated-collections")
def ROUTE_get_curated_collections():
    curated_dir = 'frontend/curated'
    dirs = os.listdir(curated_dir)
    collections = [ (dir_, os.path.getctime(f'frontend/curated/{dir_}')) for dir_ in dirs ]
    return { 'collections': collections }


# GET MOVIE
@api_router.get("/get/movie/{movie_title}")
def ROUTE_get_movie(movie_title: str):
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    movie_videos = [ vd for vd in video_objects_list if vd.movie_title and vd.movie_title.lower() == movie_title.lower() ]
    movie_videos.sort(
        key=lambda vd: (vd.date_released or '', get_sortable_string_tuple(vd.title))
    )
    return movie_videos
    

# GET MOVIE SERIES
@api_router.get("/get/movie-series/{movie_series}")
def ROUTE_get_movie_series(movie_series: str):
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    movie_videos = [ vd for vd in video_objects_list if vd.movie_series and vd.movie_series.lower() == movie_series.lower() ]
    movie_videos.sort(
        key=lambda vd: (vd.date_released or '', get_sortable_string_tuple(vd.title))
    )
    return movie_videos


# GET LINE
@api_router.get("/get/line/{line}")
def ROUTE_get_line(line: str):
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    line_videos = [ vd for vd in video_objects_list if vd.line and vd.line.lower() == line.lower() ]
    line_videos.sort(key=lambda vd: vd.date_released or '')
    return line_videos


# GET ACTOR
@api_router.get("/get/actor/{name}")
def ROUTE_get_actor(name: str):
    api_info = actor_api.get_actor_info(name)
    if api_info is None:
        api_info = actor_api.fetch_actor_info(name)
    info = {}
    if api_info:
        info = api_info
    return info



# TEMP TODO: Find better solution


# GET VIDEO COUNT
@api_router.get("/get/video-count")
def ROUTE_get_video_count():
    videos_dict = db.read_table_as_dict('videos')
    return { 'video_count': len(videos_dict) }



# GET ACTOR VIDEO COUNT
@api_router.get("/get/actor-video-count/{name}")
def ROUTE_get_actor_video_count(name: str):
    video_count = 0
    for video_data in db.read_table_as_dict('videos').values():
        if name.lower() in [ act.lower() for act in video_data.get('actors', []) ]:
            video_count += 1
    return { 'video_count': video_count }


# GET ACTOR VIDEO COUNT
@api_router.get("/get/studio-video-count/{name}")
def ROUTE_get_studio_video_count(name: str):
    name = name.lower()
    video_count = 0
    for video_data in db.read_table_as_dict('videos').values():
        for x in ['studio', 'line']:
            if name == (video_data.get(x) or '').lower():
                video_count += 1
    return { 'video_count': video_count }




# HELPERS #

def _get_random_hash_seeded(video_hashes, seed):
    from difflib import SequenceMatcher
    rng = random.Random(seed)
    gen_hash = ''
    gen_hash_len = len(video_hashes[0])
    for _ in range(gen_hash_len):
        gen_hash += hex(rng.randint(0,15))[2:]
    print('random generated hash:', gen_hash)
    return max(
        video_hashes,
        key=lambda hsh: SequenceMatcher(None, hsh, gen_hash).ratio(),
    )
    

