""" Functions for getting specific things from collection, eg. performers, studios, ... """
from ..schemas import VideoData, CatalogueQuery


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
    result['actor_counts'] =      _get_item_counts(videos_list, get_video_actors)
    result['studio_counts'] =     _get_item_counts(videos_list, get_video_studios)
    result['collection_counts'] = _get_item_counts(videos_list, get_video_collection)
    result['tag_counts'] =        _get_item_counts(videos_list, get_video_tags)
    
    # sort
    for item_type, tuple_list in result.items():
        if q.query_string and item_type == q.query_type:
            # tf-idf stuff
            ...
        else:
            result[item_type] = sorted(tuple_list, reverse=True, key=lambda x: x[1])
    
    return result



def _get_item_counts(videos_list: list[VideoData], selector_func) -> list[tuple[str, int]]:
    """  """
    item_counts = {}
    for video_data in videos_list:
        for item in selector_func(video_data):
            item = item.lower().replace('.', '').strip()
            item_counts[item] = item_counts.get(item, 0) + 1
    return [ (item, count) for item, count in item_counts.items() ]


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


