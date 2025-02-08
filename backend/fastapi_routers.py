from fastapi import APIRouter, Depends, HTTPException
import random
# from main import app # for .state

from backend.app_state import AppState


def generateReponse(main=None, time_taken=None):
    r = {}
    r['collections'] = ['main'] # state.metadataHandler.getValue('collections', [])
    r['main'] = main
    r['time_taken'] = time_taken
    return r


state = AppState()
router = APIRouter()

# Define a root endpoint
@router.get("/hello")
def read_root():
    return {"message": "Hello, World!"}

# Define another endpoint
@router.get("/items/{item_id}")
def read_item(item_id: int, q: str|None = None):
    return {"item_id": item_id, "q": q}


# region ROUTES

# GET VIDEO
@router.get("/get-video/{hash}")
def get_video(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    print("Request recieved: 'get-video', hash: ", hash)
    r = videos_dict.get(hash)
    if not r:
        print("Could not find video with hash:", hash)
        return jsonify(generateReponse()), 404
    print("Found video:", r['path'])
    if not bf.media_hasPoster(hash, MEDIADIR):
        print("Generating early poster for:", r['filename'])
        bf.media_generatePosterSimple(r['path'], hash, MEDIADIR, r['duration_seconds'])
    r['is_favourite'] = bf.is_favourite(hash, metadataHandler)
    poster = bf.media_hasPreviewThumbs(hash, MEDIADIR, small=True)
    if poster == None:
        poster = bf.media_hasPoster(hash, MEDIADIR)
    r['poster'] = poster
    # update views
    videodata = videosHandler.getValue(hash)
    videodata['views'] = videodata.get('views', 0) + 1
    videosHandler.setValue(hash, r)
    # Add viewing to metadata
    view_item = {'ts': time.time(), 'hash': hash}
    metadataHandler.appendValue('view_history', view_item)
    return jsonify(generateReponse(r)), 200



# CONFIRM SEEK THUMBNAIL
@router.get("/confirm-seek-thumbnails/{hash}")
def confirm_seek_thumbnails(hash):
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


# CONFIRM SEEK THUMBNAIL
@router.get("/confirm-poster/{hash}")
def confirm_poster(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    r = videos_dict.get(hash)
    if not r:
        print("Could not find video with hash:", hash)
        return jsonify("No video with that hash"), 404
    poster = bf.media_hasPreviewThumbs(hash, MEDIADIR, small=False)
    if poster == None:
        poster = bf.media_hasPoster(hash, MEDIADIR)
        if poster == None:
            print("Generating early poster for:", r['filename'])
            poster = bf.media_generatePosterSimple(r['path'], hash, MEDIADIR, r['duration_seconds'])
            if poster == None:
                return jsonify(generateReponse("Failed to generate poster")), 400
    custom_thumb = bf.media_hasCustomThumb(hash, CUSTOM_THUMBS_DIR)
    return_obj = {'poster': poster, 'custom_thumb': custom_thumb}
    return jsonify(generateReponse(return_obj)), 200


# CONFIRM PREVIEW THUMBNAILS
@router.get("/confirm-preview-thumbnails/<hash>")
def confirm_preview_thumbnails(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
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
@router.get("/confirm-teaser-small/<hash>")
def confirm_teaser_small(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
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
@router.get("/confirm-teaser-large/<hash>")
def confirm_teaser_large(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
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


# GET RANDOM VIDEO
@router.get("/get-random-video")
def get_random_video():
    # return {'msg': 'Not implemented', 'status_code': 404}
    # return jsonify("Not implemented"), 404
    print("Request recieved: 'get-random-video'")
    #r = random.choice([1234, 2134, 3322, 4321, "fe21acc7"])
    
    hashes = list(state.videos_dict.keys())
    print('hashes:', len(hashes))
    input('...')
    r = random.choice(hashes)
    print('random:', r)
    response = {'hash' : r}
    if not response:
        return generateReponse('Nothing!')
        return jsonify(generateReponse()), 400
    return generateReponse(response), 200

# GET RANDOM VIDEO
@router.get("/get-random-video-seeded/<seed>")
def get_random_video_seeded(seed):
    return {'msg': 'Not implemented', 'status_code': 404}
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
@router.get("/get-random-spotlight-video")
def get_random_spotlight_video():
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


# SEARCH VIDEOS
@router.get("/search-videos")
def search_videos():
    return {'msg': 'Not implemented', 'status_code': 404}
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
@router.get("/get-similar-videos/<hash>/<start_from>/<limit>")
def get_similar_videos(hash, start_from, limit):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    print("[GET SIMILAR VIDEOS] Recieved query")
    # return jsonify(generateReponse('Not implemented')), 404
    results = ff.get_similar_videos(hash, int(start_from), int(limit), videos_dict, tfidf_model)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR PERFORMERS
@router.get('/get-similar-performers/<performer>')
def get_similar_performers(performer):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    print(f'Getting similar performers to: "{performer}"')
    results = ff.get_similar_performers(performer, performer_embeddings)
    if results == None:
        jsonify(generateReponse('No results')), 400
    return jsonify(generateReponse(results)), 200


# GET SIMILAR STUDIOS
@router.get('/get-similar-studios/<studio>')
def get_similar_studio(studio):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    print(f'Getting similar studios to: "{studio}"')
    sims = [
        {'name': 'Kenna James'},
        {'name': 'AJ Applegate'},
        {'name': 'Rebeca Linares'}
    ]
    return jsonify(generateReponse(sims)), 200


# ADD FAVOURITE
@router.get("/add-favourite/<hash>")
def add_favourite(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    if bf.is_favourite(hash, metadataHandler):
        return jsonify('favourite already exists'), 200
    bf.add_favourite(hash, metadataHandler)
    return jsonify('added favourite'), 200

# REMOVE FAVOURITE
@router.get("/remove-favourite/<hash>")
def remove_favourite(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    if not bf.is_favourite(hash, metadataHandler):
        return jsonify('video already not favourites'), 200
    bf.remove_favourite(hash, metadataHandler)
    return jsonify('removed favourite'), 200

# IS FAVOURITE
@router.get("/is-favourite/<hash>")
def is_favourite(hash):
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    if bf.is_favourite(hash, metadataHandler):
        return jsonify(generateReponse({'is_favourite': True})), 200
    return jsonify(generateReponse({'is_favourite': False})), 200

# GET ALL PERFORMERS
@router.get("/get-performers")
def get_performers():
    return {'msg': 'Not implemented', 'status_code': 404}
    # return jsonify("Not implemented"), 404
    print(len(state.videos_dict))
    items = ff.getPerformers(state.videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500

# GET ALL STUDIOS
@router.get("/get-studios")
def get_studios():
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    items = ff.getStudios(videos_dict)
    print('Len of items:', len(items))
    if items:
        return jsonify(generateReponse(items)), 200
    return jsonify(), 500


# GIF METHODS

# CREATE NEW GIF
@router.get("/create-new-gif-random")
def create_new_gif_random():
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    global gifManager
    try:
        new_gifs = gifManager.generate_new_gifs(
            request.args.get('video_hash'),
            request.args.get('include_tags', [])
        )
        if new_gifs == None:
            return jsonify('Cannot find video with that hash'), 404
        return jsonify(generateReponse(new_gifs)), 200
    except Exception as e:
        print("EXCEPTION with GifManager:")
        print(e)
        return jsonify('Internal error'), 500

# GET RANDOM GIF
@router.get("/get-random-gif")
def get_random_gif():
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    global gifManager
    try:
        rand_gif = gifManager.get_random_gif(
            request.args.get('video_hash'),
            request.args.get('include_tags', [])
        )
        if rand_gif == None:
            return jsonify('Cannot find video with that hash'), 404
        return jsonify(generateReponse(rand_gif)), 200
    except Exception as e:
        print("EXCEPTION with GifManager:")
        print(e)
        return jsonify('Internal error'), 500

# DELETE GIF
@router.get("/delete_gif")
def delete_gif():
    return {'msg': 'Not implemented', 'status_code': 404}
    return jsonify("Not implemented"), 404
    global gifManager
    args = request.args
    return jsonify('Not implemented'), 404


# endregion