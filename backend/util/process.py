""" Process videos (hashing, filename parsing, metadata getting, ...) """
import os
import time
from pathlib import Path
from dataclasses import fields

from handymatt import StringParser
from handymatt_media import video_analyser
from handymatt_media.metadata import video_metadata

from ..data.video_data import VideoData

#region ### PUBLIC ###

def process_videos(
    video_paths: list[str],
    existing_videos: dict[str, VideoData],
    collections_dict: dict[str, str],
    scene_filename_formats: list[str],
    rehash_videos = False,
    # readd_video_attributes = False, # TODO: rename!
) -> dict[str, VideoData]:
    """
    Given a list of video path and a dictionary of previously scanned video data objects,
    find existing video data by filename, if needed, hash video, and process video. 
    Returns -> dict with all processed videos
    """
    
    videos_dict: dict[str, VideoData] = {}
    hash_path_map: dict[str, str] = _get_video_hashes(video_paths, existing_videos, rehash_videos=rehash_videos)
    # hash_path_map: dict[str, str] = _get_video_hashes_multi(video_paths, existing_videos, rehash_videos=rehash_videos)

    # process videos
    parser = StringParser(scene_filename_formats)
    for idx, (video_hash, video_path) in enumerate(hash_path_map.items()):
        print('\rprocessing videos ({:_}/{:_})'.format(idx+1, len(hash_path_map)), end='')
        video_data: VideoData|None = existing_videos.get(video_hash)
        if video_data is None:
            video_data = _get_new_video_data_object(video_hash, video_path)
        
        video_data.path = video_path
        video_data.filename = Path(video_path).name
        video_data = _add_collection_attributes(video_data, collections_dict)
        
        # add data parsed from filename / path
        video_data = _add_filename_parsed_data(video_data, parser)
        
        # read tags from json file and add them
        ...
        
        # organize tags
        ...
    print()

    return videos_dict


#region ### PRIVATE ###

def _get_video_hashes(
    video_paths: list[str],
    existing_videos: dict[str, VideoData],
    rehash_videos = False
) -> dict[str, str]:
    """ Gets video hashes for a list of video paths and a dict of existing video data objects """

    hash_path_map: dict[str, str] = {}
    hashing_failed, had_to_hash, collisions = [], [], []
    path_hash_map = { video_data.path: hash for hash, video_data in existing_videos.items() }
    for idx, video_path in enumerate(video_paths):
        print('\rgetting video hash ({:_}/{:_})'.format(idx+1, len(video_paths)), end='')
        video_hash: str|None = path_hash_map.get(video_path)
        if video_hash is None: # get hash from metadata
            video_hash = _get_hash_from_video_metadata(video_path)
        if video_hash is None or rehash_videos:
            had_to_hash.append(video_path)
            try:
                video_hash = video_analyser.getVideoHash_ffmpeg(video_path)
            except Exception as e:
                hashing_failed.append(video_path)
            if video_hash: # add hash to metadata
                _add_hash_to_video_metadata(video_path, video_hash)
        # if video_hash is None:
        else:
            if video_hash in hash_path_map:
                collisions.append(video_hash)
            else:
                hash_path_map[video_hash] = video_path
    print()
    # print hashing report
    return hash_path_map



def _get_new_video_data_object(
        video_hash: str, 
        video_path: str, 
    ) -> VideoData:
    """ Get initial video data object. Add only hash, path, filename, and video attributes """
    
    extracted_data = video_analyser.getVideoData(video_path)
    video_data = VideoData(
        hash = video_hash,
        path = video_path,
        date_added = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getctime(video_path))), # ctime
        duration =          extracted_data['duration'],
        duration_seconds =  extracted_data['duration_seconds'],
        filesize_mb =       extracted_data['filesize_mb'],
        fps =               extracted_data['fps'],
        resolution =        extracted_data['resolution'],
        bitrate =           extracted_data['bitrate'],
    )
    return video_data


def _add_collection_attributes(data: VideoData, collections_dict: dict) -> VideoData:
    """ Determine collection and add collection attributes 
        (collection, parent_dir, path_relative) to VideoDict """
    parent_dir = None
    collections_dict_paths = sorted(collections_dict.keys(), reverse=True, key=lambda path: len(path))
    for collection_dir in reversed(collections_dict_paths):
        if data.path.startswith(collection_dir):
            parent_dir = collection_dir  # may happen more than once
    collection = collections_dict.get(parent_dir)
    if collection is None or parent_dir is None:
        raise KeyError('Collection not defined for parentdir: "{}"'.format(parent_dir))
    
    data.collection = collection
    data.parent_dir = parent_dir
    data.path_relative = str(Path(data.path).relative_to(Path(parent_dir)))
    return data


""" 
TAGS:
    tags_from_path = [ p.replace('_', '') for p in path_relative.split(os.sep)[:-1] if p != '' ]
    obj['tags_from_path'] = [ t for t in tags_from_path if (t not in obj.get('performers', []) and t != obj.get('studio', '')) ]
    tags = obj.get('tags', [])
    tags.extend(obj['tags_from_path'])
    obj['tags'] = sorted(set(tags))
    
"""



def _add_filename_parsed_data(data: VideoData, parser: StringParser):
    """ Parse data from video filename, format slightly, and add to VideoData """

    path_obj = Path(data.path)
    scene_info = _parse_filename(path_obj.stem, parser)
    if len(scene_info) == 1:  # matched only title, using dirname as sort_performers
        fn = "{} - {}".format(path_obj.parent.name, path_obj.stem)
        scene_info = _parse_filename(fn, parser)
    
    scene_info = _filter_scene_info(scene_info)
    
    data = _update_dataclass_from_dict(data, scene_info)
    
    return data


def _filter_scene_info(info: dict) -> dict:
    # use year if no date_released
    if info.get('date_released') is None and 'year' in info:
        info['date_released'] = str(info['year'])
        del info['year']
    
    # add tags from filename
    if 'tags' in info:
        info['tags_from_filename'] = info['tags']
        del info['tags']
    
    # combine performers
    if 'sort_performers' in info:
        info['sort_performers'] = info['sort_performers'].split(", ")
    if 'mention_performers' in info:
        info['mention_performers'] = info['mention_performers'].split(', ')
    performers = info.get('sort_performers', []) + info.get('mention_performers', [])
    info['performers'] = _get_ordered_set(performers)
    
    return info


def _parse_filename(filename: str, parser: StringParser):
    info = parser.parse(filename)
    if info is None:
        raise TypeError('String parser returned `None` for filename: "{}"'.format(filename))
    return info


#region ### HELPERS ###

def _update_dataclass_from_dict(instance, update_dict: dict):
    for key, value in update_dict.items():
        if key in {field.name for field in fields(instance)}:
            setattr(instance, key, value)
        else:
            raise Exception('Key not found in dataclass: "{}"'.format(key))
    return instance

# list of unique items which preserves order of original list
def _get_ordered_set(arr):
    newarr = []
    seen = set()
    for item in arr:
        if item not in seen:
            newarr.append(item)
            seen.add(item)
    return newarr


_CPOP_HASH_KEY = 'candypop_hash'

def _get_hash_from_video_metadata(video_path: str) -> str|None:
    if Path(video_path).suffix == '.mkv':
        tags = video_metadata.getMetadataTags_MKV(video_path)
        return tags.get(_CPOP_HASH_KEY)
    return None

def _add_hash_to_video_metadata(video_path: str, video_hash: str):
    if Path(video_path).suffix == '.mkv':
        tags = { _CPOP_HASH_KEY: video_hash }
        video_metadata.addMetadataTags_MKV(video_path, tags)

