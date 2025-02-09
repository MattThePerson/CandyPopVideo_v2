""" Functions related to video searching """
import random
import time
from datetime import datetime

from .tfidf import get_related_videos_from_query_TFIDF, STOPWORDS_ENG
from ..util import backendFun as bf


# search, filter and sort videos
def searchVideosFunction(videos: list[dict], search_params: dict, metadataHandler, tfidf_model, token_hashes) -> dict | None:
    """ Get video results given filters and search query """
    search_query, actor, studio, collection, include_terms, exclude_terms, date_added_from, date_added_to, date_released_from, date_released_to, only_favourites, sort_by = [ 
        search_params.get(x) for x in ['search', 'actor', 'studio', 'collection', 'include_terms', 'exclude_terms', 'date_added_from', 'date_added_to', 'date_released_from', 'date_released_to', 'only_favourites', 'sort_by']
    ]
    limit =     int( search_params.get('limit', 12) )
    startfrom = int( search_params.get('startfrom', 0) )
    favs = only_favourites == 'true'
    include_terms = [ x.lower().strip() for x in include_terms.split(',') ] if include_terms else []
    exclude_terms = [ x.lower().strip() for x in exclude_terms.split(',') ] if exclude_terms else []

    # videos = list(videos_dict.values())
    videos.sort(reverse=True, key=lambda video: (
        video['date_added']
    ))
    
    # search videos
    if search_query:
        # videos = searchVideos_tokenHashes(videos, search_query, token_hashes)
        videos = searchVideos_TFIDF(videos, search_query, tfidf_model)
    
    # filter videos
    videos = _filterVideos(videos, favs, actor, studio, collection, date_added_from, date_added_to, date_released_from, date_released_to, include_terms, exclude_terms, metadataHandler)
    if len(videos) < startfrom:
        return None

    # sort videos
    if sort_by and not search_query:
        videos = _sortVideos(videos, sort_by)

    word_cloud = _generate_word_cloud(videos, studio, actor, collection, include_terms)

    results_object = {
        'videos' : videos[startfrom: startfrom+limit],
        'amount_of_results' : len(videos),
        'word_cloud' : word_cloud
    }
    return results_object

# search videos TFIDF
def searchVideos_TFIDF(video_objects: list[dict], search_query: str, tfidf_model):
    """ Get sorted and filtered list of video objects based on TF-IDF score for search query cast into TD-IDF feature space """
    print("\n[TFIDF] Finding related videos for query: '{}'".format(search_query))
    start = time.time()
    # related_hashes, _ = get_related_hashes_from_query(token_hashes, search_query)
    related_hashes = get_related_videos_from_query_TFIDF(search_query, tfidf_model)
    print("  Done (took {}ms)".format(int((time.time()-start)*1_000)))
    hash_scores = { hash: score for hash, score in related_hashes if score > 0 }
    video_objects = [ vid for vid in video_objects if vid['hash'] in hash_scores ]
    video_objects.sort( reverse=True, key=lambda vid: hash_scores[vid['hash']] )
    return video_objects


# filter videos
def _filterVideos(filtered, favs, actor, studio, collection, date_added_from, date_added_to, date_released_from, date_released_to, include_terms, exclude_terms, metadataHandler={}):
    
    if favs:            filtered = [ vid for vid in filtered if ( bf.is_favourite(vid['hash'], metadataHandler) ) ]
    if actor:           filtered = [ vid for vid in filtered if ( _actor_in_video(actor, vid) ) ]
    if studio:          filtered = [ vid for vid in filtered if ( ( vid.get('studio') and studio.lower() in vid['studio'].lower() ) ) ]
    if collection:      filtered = [ vid for vid in filtered if ( (vid['collection'] and collection.lower() in vid['collection'].lower()) ) ]

    if date_added_from:     filtered = [ vid for vid in filtered if ( (_get_video_date_released(vid) and _get_video_date_released(vid) >= date_added_from) ) ]
    if date_added_to:       filtered = [ vid for vid in filtered if ( (_get_video_date_released(vid) and _get_video_date_released(vid) < date_added_to) ) ]
    if date_released_from:  filtered = [ vid for vid in filtered if ( (vid.get('date_released') and vid['date_released'] >= date_released_from) ) ]
    if date_released_to:    filtered = [ vid for vid in filtered if ( (vid.get('date_released') and vid['date_released'] < date_released_to) ) ]

    for term in include_terms:  filtered = [ vid for vid in filtered if ( term in vid['path'].lower() ) ]
    for term in exclude_terms:  filtered = [ vid for vid in filtered if ( term not in vid['path'].lower() ) ]

    return filtered


# sort videos
def _sortVideos(videos, sort_by):
    videos.sort(
        reverse=False,
        key=lambda video: ( (video.get(sort_by) is None) != False, video.get('title', '') )
    )
    if sort_by == 'random':
        random.seed(str(datetime.now()))
        random.shuffle(videos)
    else:
        sort_reverse = ('desc' in sort_by)
        for x in ['-asc', '-desc']:
            sort_by = sort_by.replace(x, '')
        sort_by = sort_by.replace('-', '_')
        if sort_by == 'date_released':
            videos.sort(
                reverse=sort_reverse,
                key=lambda video: ( (video.get(sort_by) is None) != sort_reverse, _get_video_date(video) ) # tuple where first element if boolean. 
            )
        else:
            videos.sort(
                reverse=sort_reverse,
                key=lambda video: ( (video.get(sort_by) is None) != sort_reverse, video.get(sort_by) ) # tuple where first element if boolean. 
            )
    return videos


# generate word cloud
def _generate_word_cloud(videos, studio, actor, collection, include_terms, size_limit=20_000):
    word_cloud = []
    if len(videos) < size_limit:
        wc_exclude_terms = [ term.lower() for term in [studio, actor, collection] + include_terms if term != None ]
        word_cloud = get_word_cloud(videos, exclude_terms=wc_exclude_terms)
    return word_cloud

def get_word_cloud(videos, exclude_terms=[]):
    print('[GET_WORD_CLOUD] Calculating word cloud ... ', end='')
    start = time.time()
    word_cloud = {}
    for vid in videos:
        tokens = []
        title = vid.get('title')
        parts_title = []
        if title:
            parts_title = get_preprocessed_text(title)
            parts_title.extend(get_bigrams(parts_title))
        tokens.extend(parts_title)
        tokens.extend(vid['performers'])
        tokens.extend(vid.get('mention_performer', '').split(', '))
        tokens.append(vid.get('studio', ''))
        tokens.extend(vid.get('tags', ''))
        tokens.extend(vid.get('tags_from_path', ''))
        tokens = [
            t.lower() for t in set(tokens)
            if (len(t) > 1) and not t.isnumeric() and (t.lower() not in ['', 'vol', 'scene', 'part', 'mkv', 'mp4', 'com', 'xxx', 'episode']) and (t.lower() not in exclude_terms) and t not in STOPWORDS_ENG
            and 'scene' not in t.lower() and 'part' not in t.lower()
        ]
        for t in tokens:
            word_cloud[t] = word_cloud.get(t, 0) + 1
    word_cloud = [ (k, v) for k, v in word_cloud.items() if v > 1 ]
    word_cloud.sort(reverse=True, key=lambda x: x[1])
    print('took {:.3f}s'.format(time.time()-start))
    return word_cloud

def get_preprocessed_text(s) -> list[str]:
    s = s.lower()
    s = s.lower()
    for c in '[]()-_!,.\\&':
        s = s.replace(c, ' ')
    return [ p for p in s.split() if p not in [''] ]

def get_bigrams(parts):
    bigrams = []
    for i in range(len(parts)-1):
        bg = '{} {}'.format(parts[i], parts[i+1])
        bigrams.append(bg)
    return bigrams



### HELPERS ###

def _get_video_date_released(vid):
    if 'date_released_d18':
        return vid['date_released_d18']
    return vid.get('date_released')

def _actor_in_video(actor, vid):
        actor = actor.lower()
        performers_str = ''
        if 'performers' in vid and vid['performers'] != None:
            performers_str = ", ".join(vid['performers']).lower()
        mention_performers = ''
        if 'mention_performer' in vid and vid['mention_performer'] != None:
            mention_performers = vid['mention_performer'].lower()
        return actor in performers_str or actor in mention_performers

def _get_video_date(video):
    if 'date_released_d18' in video:
        return video['date_released_d18']
    return video['date_released']

