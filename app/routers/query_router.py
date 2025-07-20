""" Routes for searching videos """
import time
from fastapi import APIRouter, HTTPException

from .. import db
from config import TFIDF_MODEL_PATH
from ..schemas import SearchQuery, VideoData, VideoInteractions, CatalogueQuery
from ..recommender import search, similarity
from ..recommender.catalogue import get_catalogue
from ..util.general import pickle_load


query_router = APIRouter()

# SEARCH VIDEOS
@query_router.post("/search-videos")
def ROUTE_search_videos(query: SearchQuery):
    video_dicts = db.read_table_as_dict('videos')
    video_objects_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    video_interactions = { hsh: VideoInteractions.from_dict(vd) for hsh, vd in db.read_table_as_dict('interactions').items() }
    tfidf_model = pickle_load(TFIDF_MODEL_PATH)
    start = time.time()
    search_results_tuple = search.searchVideos(
        video_objects_list,
        query,
        video_interactions,
        tfidf_model,
        None,
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
def ROUTE_get_similar_videos(video_hash: str, start_from: int, limit: int):
    
    tfidf_model = pickle_load(TFIDF_MODEL_PATH)
    if tfidf_model is None:
        print("TF-IDF model doesn't exist")
        raise HTTPException(status_code=503, detail="TF-IDF model doesn't exist")
    
    video_dicts = db.read_table_as_dict('videos')
    videos_list = [ VideoData.from_dict(dct) for dct in video_dicts.values() ]
    video_results, amount_of_results = similarity.get_similar_videos(video_hash, start_from, limit, videos_list, tfidf_model)
    video_dict_results = [ vd.to_dict() for vd in video_results ]
    if amount_of_results == 0:
        print('UNEXPECTED: Got 0 similar videos')
        raise HTTPException(status_code=404, detail="No similar videos found")
    
    return {
        'search_results': video_dict_results,
        'amount_of_results': amount_of_results,
    }


# GET SIMILAR PERFORMERS
@query_router.get('/get/similar-actors/{performer}')
def ROUTE_get_similar_performers(performer: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    print(f'Getting similar performers to: "{performer}"')
    results = ff.get_similar_performers(performer, performer_embeddings)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR STUDIOS
@query_router.get('/get/similar-studios/{studio}')
def ROUTE_get_similar_studio(studio: str):
    raise HTTPException(status_code=501, detail='Not implemented')
    return jsonify("Not implemented"), 404
    print(f'Getting similar studios to: "{studio}"')
    return jsonify(generateReponse(sims)), 200


# 
@query_router.post('/get/catalogue')
def ROUTE_get_catalogue(query: CatalogueQuery):
    # raise HTTPException(status_code=501, detail='Not implemented')
    video_dicts = db.read_table_as_dict('videos')
    videos_list = [ VideoData.from_dict(vd) for vd in video_dicts.values() if vd.get('is_linked') ]
    print('[catalogue] getting catalogue')
    start = time.time()
    result: dict = {}
    result = get_catalogue(videos_list, query)
    # try:
    # except Exception as e:
    #     print("[catalogue] Exception:", e)
    #     raise HTTPException(status_code=500, detail="Exception while getting catalogue")
    tt = time.time() - start
    print('[catalogue] done. took {:.1f} sec'.format(tt))
    result['time_taken'] = tt
    return result

