from fastapi import APIRouter, Response


search_router = APIRouter()


# SEARCH VIDEOS
@search_router.get("/search-videos")
def search_videos():
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    print("[SEARCH] Recieved query")
    start = time.time()
    results = ff.searchVideosFunction(videos_dict, request.args, metadataHandler, tfidf_model, None)
    if results == None:
        jsonify(generateReponse()), 400
    results['time_taken'] = round( time.time()-start, 3 )
    print(results['time_taken'])
    return jsonify(generateReponse(results)), 200


# GET SIMILAR VIDEOS
@search_router.get("/get-similar-videos/{video_hash}/{start_from}/{limit}")
def get_similar_videos(video_hash: str, start_from: int, limit: int):
    return Response('Not yet implemented', 501)
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    print("[GET SIMILAR VIDEOS] Recieved query")
    # return jsonify(generateReponse('Not implemented')), 404
    results = ff.get_similar_videos(hash, int(start_from), int(limit), videos_dict, tfidf_model)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR PERFORMERS
@search_router.get('/get-similar-performers/{performer}')
def get_similar_performers(performer: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    print(f'Getting similar performers to: "{performer}"')
    results = ff.get_similar_performers(performer, performer_embeddings)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR STUDIOS
@search_router.get('/get-similar-studios/{studio}')
def get_similar_studio(studio: str):
    return Response('Not yet implemented', 501)
    return jsonify("Not implemented"), 404
    print(f'Getting similar studios to: "{studio}"')
    sims = [
        {'name': 'Kenna James'},
        {'name': 'AJ Applegate'},
        {'name': 'Rebeca Linares'}
    ]
    return jsonify(generateReponse(sims)), 200

