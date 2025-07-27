""" Functions for getting specific things from collection, eg. performers, studios, ... """
from datetime import datetime

from src.schemas import VideoData, CatalogueQuery


def get_catalogue(videos_list: list[VideoData], query: CatalogueQuery) -> dict[str, list[tuple[str, int]]]:
    """
    For a given set of filters (performer, studio, collection, tags), for each
    category return map of scene counts. 
    """
    
    q = query
    
    # apply sort performers choice
    if q.use_primary_actors:
        get_video_actors = get_video_primary_actors
    else:
        get_video_actors = get_video_actors_all

    # filter
    if q.filter_actor:        videos_list = [ vd for vd in videos_list if q.filter_actor in         get_video_actors(vd) ]
    if q.filter_studio:       videos_list = [ vd for vd in videos_list if q.filter_studio in        get_video_studios(vd) ]
    if q.filter_collection:   videos_list = [ vd for vd in videos_list if q.filter_collection in    get_video_collection(vd) ]
    if q.filter_tag:          videos_list = [ vd for vd in videos_list if q.filter_tag in           get_video_tags(vd) ]
    
    # get item counts
    result = {}
    result['actor_info'] =      _get_item_info(videos_list, get_video_actors)
    result['studio_info'] =     _get_item_info(videos_list, get_video_studios)
    result['collection_info'] = _get_item_info(videos_list, get_video_collection)
    result['tag_info'] =        _get_item_info(videos_list, get_video_tags)
    
    # sort
    for item_type, tuple_list in result.items():
        if q.query_string and item_type == q.query_type:
            # tf-idf stuff
            ...
        else:
            result[item_type] = sorted(tuple_list, reverse=True, key=lambda x: x[1])
    
    return result



def _get_item_info(videos_list: list[VideoData], selector_func) -> list[tuple]:
    """  """
    item_counts = {}
    newest_video = {}
    oldest_video = {}
    new_videos = {}
    for video_data in videos_list:
        for item in selector_func(video_data):
            item = item.lower().replace('.', '').strip()
            item_counts[item] = item_counts.get(item, 0) + 1
            newest_video[item] = max( newest_video.get(item, '0000'), video_data.date_added )
            oldest_video[item] = min( oldest_video.get(item, '2100'), video_data.date_added )
            if seconds_from_now(video_data.date_added) < (60*60*24*7): # a week old
                new_videos[item] = new_videos.get(item, 0) + 1
    return [
        (item, item_counts.get(item), newest_video.get(item), new_videos.get(item))
        for item in item_counts.keys()
    ]


def get_video_actors_all(vd: VideoData) -> list[str]:
    return vd.actors

def get_video_primary_actors(vd: VideoData) -> list[str]:
    return vd.primary_actors

def get_video_studios(vd: VideoData) -> list[str]:
    return [ x for x in [vd.studio, vd.line] if x is not None ]

def get_video_collection(vd: VideoData) -> list[str]:
    if vd.collection:
        return [vd.collection]
    return []

def get_video_tags(vd: VideoData) -> list[str]:
    return vd.tags


# HELPERS

def seconds_from_now(date: str) -> int:
    fmt = "%Y-%m-%d %H:%M"
    curr = datetime.now().strftime(fmt)
    return _dates_difference(date, curr, fmt=fmt)

def _dates_difference(d1: str, d2: str, fmt="%Y-%m-%d %H:%M") -> int:
    dt1 = datetime.strptime(d1, fmt)
    dt2 = datetime.strptime(d2, fmt)
    return int((dt2 - dt1).total_seconds())
