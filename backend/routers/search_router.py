""" Routes for searching videos """
import time
from fastapi import APIRouter, Response
from pydantic import BaseModel

from ..search.search import searchVideosFunction

class Query(BaseModel):
    search_query: str|None
    include_tags: list[str]
    exclude_tags: list[str]
    sortby: str|None
    # datetime_earliest: str
    # datetime_latest: str

search_router = APIRouter()

# SEARCH VIDEOS
@search_router.post("/query/search-videos")
def search_videos(query: Query):
    return Response('Not implemented', 501)
    params = dict(request.query_params)
    # print(params)
    # return Response('Not yet implemented', 501)
    start = time.time()
    # videos = list(state.videos_dict.values())
    videos = [ vid.to_dict() for vid in state.videos_dict.values() ]
    results = searchVideosFunction(videos, params, state.metadataHandler, state.tfidf_model, None)
    if results is None:
        return Response('Failed to get results', 404)
    results['time_taken'] = round( time.time()-start, 3 )
    return { 'main': results }


# GET SIMILAR VIDEOS
@search_router.get("/query/get-similar-videos/{video_hash}/{start_from}/{limit}")
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
@search_router.get('/query/get-similar-performers/{performer}')
def get_similar_performers(performer: str):
    return Response('Not implemented', 501)
    print(f'Getting similar performers to: "{performer}"')
    results = ff.get_similar_performers(performer, performer_embeddings)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR STUDIOS
@search_router.get('/query/get-similar-studios/{studio}')
def get_similar_studio(studio: str):
    return Response('Not implemented', 501)
    return jsonify("Not implemented"), 404
    print(f'Getting similar studios to: "{studio}"')
    return jsonify(generateReponse(sims)), 200

