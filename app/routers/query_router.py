""" Routes for searching videos """
import time
from fastapi import APIRouter, Response, HTTPException

from ..recommender.search import searchVideosFunction
from ..schemas import SearchQuery, VideoData
from .. import db

query_router = APIRouter()

# SEARCH VIDEOS
@query_router.post("/search-videos")
def search_videos(query: SearchQuery):
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    start = time.time()
    search_results_tuple = searchVideosFunction(
        video_objects_list,
        query,
        {}, #state.metadataHandler,
        [], #state.tfidf_model
        None
    )
    if search_results_tuple is None:
        raise HTTPException(status_code=500, detail='Failed to get results')
    (results, videos_filtered_count, word_cloud) = search_results_tuple
    return {
        'search_results': results,
        'videos_filtered_count': videos_filtered_count,
        'word_cloud': word_cloud,
        'time_taken': round( time.time()-start, 3 ),
    }


# GET SIMILAR VIDEOS
@query_router.get("/get/similar-videos/{video_hash}/{start_from}/{limit}")
def get_similar_videos(video_hash: str, start_from: int, limit: int):
    raise HTTPException(status_code=501, detail='Not implemented')
    # return jsonify(generateReponse('Not implemented')), 404
    # results = ff.get_similar_videos(hash, int(start_from), int(limit), videos_dict, tfidf_model)
    # if results == None:
    #     jsonify(generateReponse('No results')), 400
    # return jsonify(generateReponse(results)), 200


# GET SIMILAR PERFORMERS
@query_router.get('/get/similar-performers/{performer}')
def get_similar_performers(performer: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    print(f'Getting similar performers to: "{performer}"')
    results = ff.get_similar_performers(performer, performer_embeddings)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR STUDIOS
@query_router.get('/get/similar-studios/{studio}')
def get_similar_studio(studio: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    return jsonify("Not implemented"), 404
    print(f'Getting similar studios to: "{studio}"')
    return jsonify(generateReponse(sims)), 200

