""" Routes for searching videos """
import time
from fastapi import APIRouter, Response

from ..recommender.search import searchVideosFunction
from ..schemas import SearchQuery, VideoData
from .. import db

query_router = APIRouter()

# SEARCH VIDEOS
@query_router.post("/query/search-videos")
def search_videos(query: SearchQuery):
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() ]
    start = time.time()
    search_results_tuple = searchVideosFunction(
        video_objects_list,
        query,
        {}, #state.metadataHandler,
        [], #state.tfidf_model
        None
    )
    if search_results_tuple is None:
        return Response('Failed to get results', 500)
    (results, videos_filtered_count, word_cloud) = search_results_tuple
    return {
        'results': results,
        'videos_filtered_count': videos_filtered_count,
        'word_cloud': word_cloud,
        'time_taken': round( time.time()-start, 3 ),
    }


# GET SIMILAR VIDEOS
@query_router.get("/query/get-similar-videos/{video_hash}/{start_from}/{limit}")
def get_similar_videos(video_hash: str, start_from: int, limit: int):
    print('video_hash:', video_hash)
    return Response('Not implemented', 501)
    print("[GET SIMILAR VIDEOS] Recieved query")
    # return jsonify(generateReponse('Not implemented')), 404
    results = ff.get_similar_videos(hash, int(start_from), int(limit), videos_dict, tfidf_model)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR PERFORMERS
@query_router.get('/query/get-similar-performers/{performer}')
def get_similar_performers(performer: str):
    return Response('Not implemented', 501)
    print(f'Getting similar performers to: "{performer}"')
    results = ff.get_similar_performers(performer, performer_embeddings)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR STUDIOS
@query_router.get('/query/get-similar-studios/{studio}')
def get_similar_studio(studio: str):
    return Response('Not implemented', 501)
    return jsonify("Not implemented"), 404
    print(f'Getting similar studios to: "{studio}"')
    return jsonify(generateReponse(sims)), 200

