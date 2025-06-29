""" Functions related to video searching """
import random
import time
from datetime import datetime

from .tfidf import get_related_videos_from_query_TFIDF, STOPWORDS_ENG
from ..util import _favourites
from ..schemas import SearchQuery, VideoData

from handymatt import JsonHandler

# TODO: convert videos to list[VideoData]

# search, filter and sort videos
# metadataHandler: JsonHandler
# tfidf_model: tuple?
def searchVideosFunction(videos_list: list[VideoData], search_query: SearchQuery, metadata: dict, tfidf_model, token_hashes) -> tuple[list, int, list] | None:
    """ Filter and sort a list of VideoData given a SearchQuery and TF-IDF model """
    q = search_query
    
    if q.limit is None:     q.limit = 12
    if q.startfrom is None: q.startfrom = 0
    
    # sort by date added
    videos_list.sort(reverse=True, key=lambda video: (
        video.date_added
    ))
    
    # search videos
    if q.search_string:
        # # videos_list = searchVideos_tokenHashes(videos_list, search_string, token_hashes)
        # videos_list = searchVideos_TFIDF(videos_list, q.search_string, tfidf_model) # TODO: Re-enable and fix TF-IDF
        ...
    
    # filter videos
    videos_list = filterVideoObjects(videos_list, q, metadata)
    if len(videos_list) < q.startfrom:
        return None

    # sort videos
    if q.sortby and not q.search_string:
        videos_list = _sortVideos(videos_list, q.sortby)

    # return
    word_cloud = _generate_word_cloud(videos_list, q.studio, q.performer, q.collection, q.include_terms)
    limited_results = videos_list[ q.startfrom: q.startfrom+q.limit ]
    videos_filtered_count = len(videos_list)
    return limited_results, videos_filtered_count, word_cloud

    results_object = {
        'videos' : videos[startfrom: startfrom+limit],
        'amount_of_results' : len(videos),
        'word_cloud' : word_cloud
    }
    # return results_object





# search videos TFIDF
def searchVideos_TFIDF(video_objects: list[VideoData], search_query: str, tfidf_model):
    """ Get sorted and filtered list of video objects based on TF-IDF score for search query cast into TD-IDF feature space """
    print("\n[TFIDF] Finding related videos for query: '{}'".format(search_query))
    start = time.time()
    # related_hashes, _ = get_related_hashes_from_query(token_hashes, search_query)
    related_hashes = get_related_videos_from_query_TFIDF(search_query, tfidf_model)
    print("  Done (took {}ms)".format(int((time.time()-start)*1_000)))
    hash_scores = { hash: score for hash, score in related_hashes if score > 0 }
    video_objects = [ vid for vid in video_objects if vid.hash in hash_scores ]
    video_objects.sort( reverse=True, key=lambda vid: hash_scores[vid.hash] )
    return video_objects




# filter videos
def filterVideoObjects(filtered: list[VideoData], search_query: SearchQuery, metadata: dict={}):
    
    q = search_query
    
    if q.only_favourites:     filtered = [ vid for vid in filtered if ( _favourites.is_favourite(vid.hash, metadata) ) ]
    if q.performer:               filtered = [ vid for vid in filtered if ( _actor_in_video(q.performer, vid) ) ]
    if q.studio:              filtered = [ vid for vid in filtered if ( ( vid.studio and vid.studio.lower() in q.studio.lower() ) ) ]
    if q.collection:          filtered = [ vid for vid in filtered if ( (vid.collection and q.collection.lower() in vid.collection.lower()) ) ]

    if q.date_added_from:     filtered = [ vid for vid in filtered if ( (vid.date_added >= q.date_added_from) ) ]
    if q.date_added_to:       filtered = [ vid for vid in filtered if ( (vid.date_added < q.date_added_to) ) ]
    if q.date_released_from:  filtered = [ vid for vid in filtered if ( (vid.date_released and vid.date_released >= q.date_released_from) ) ]
    if q.date_released_to:    filtered = [ vid for vid in filtered if ( (vid.date_released and vid.date_released < q.date_released_to) ) ]

    include_terms = [ t.lower() for t in q.include_terms ]
    for t_lower in include_terms:  filtered = [ vid for vid in filtered if ( t_lower in vid.path.lower() ) ]
    exclude_terms = [ t.lower() for t in q.exclude_terms ]
    for t_lower in exclude_terms:  filtered = [ vid for vid in filtered if ( t_lower not in vid.path.lower() ) ]
    
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
def _generate_word_cloud(videos: list[VideoData], studio, actor, collection, include_terms, size_limit=20_000):
    word_cloud = []
    if len(videos) < size_limit:
        wc_exclude_terms = [ term.lower() for term in [studio, actor, collection] + include_terms if term != None ]
        word_cloud = get_word_cloud(videos, exclude_terms=wc_exclude_terms)
    return word_cloud

def get_word_cloud(videos: list[VideoData], exclude_terms=[]) -> list[tuple[str, int]]:
    print('[GET_WORD_CLOUD] Calculating word cloud ... ', end='')
    start = time.time()
    word_cloud_dict: dict[str, int] = {}
    for vid in videos:
        tokens = []
        title = vid.scene_title
        parts_title = []
        if title:
            parts_title = get_preprocessed_text(title)
            parts_title.extend( get_bigrams(parts_title) )
        tokens.extend(parts_title)
        tokens.extend(vid.performers)
        tokens.extend(vid.mention_performers)
        tokens.extend(vid.tags)
        tokens.extend(vid.tags_from_path)
        if vid.studio: tokens.append(vid.studio)
        tokens = [
            t.lower() for t in set(tokens)
            if (len(t) > 1) and not t.isnumeric() and (t.lower() not in ['', 'vol', 'scene', 'part', 'mkv', 'mp4', 'com', 'xxx', 'episode']) and (t.lower() not in exclude_terms) and t not in STOPWORDS_ENG
            and 'scene' not in t.lower() and 'part' not in t.lower()
        ]
        for t in tokens:
            word_cloud_dict[t] = word_cloud_dict.get(t, 0) + 1
    word_cloud = [ (k, v) for k, v in word_cloud_dict.items() if v > 1 ]
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

def _actor_in_video(actor: str, vid: VideoData):
        actor = actor.lower()
        if vid.performers != None:
            for perf in vid.performers:
                if actor == perf.lower():
                    return True
        return False

def _get_video_date(video):
    if 'date_released_d18' in video:
        return video['date_released_d18']
    return video['date_released']

