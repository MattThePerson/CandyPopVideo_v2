""" Process videos (hashing, filename parsing, metadata getting, ...) """
import os
import re
import time
from pathlib import Path
from dataclasses import fields

from handymatt import StringParser
from handymatt_media import video_analyser
from handymatt_media.metadata import video_metadata

from ..schemas.video_data import VideoData
from ..loggers import LOGGER_HASHING_FAILED, LOGGER_COLLISIONS


#region - PUBLIC -------------------------------------------------------------------------------------------------------

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
    # hash_path_map: dict[str, str] = _get_video_hashes_multi(video_paths, existing_videos, rehash_videos=rehash_videos) # multithreaded

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
        
        videos_dict[video_hash] = video_data
    print()

    return videos_dict


#region - PRIVATE ------------------------------------------------------------------------------------------------------

def _get_video_hashes(
    video_paths: list[str],
    existing_videos: dict[str, VideoData],
    rehash_videos: bool=False,
) -> dict[str, str]:
    """ For a list of video paths, try to find their hash from exisiting videos, or else rehash. Return map[hash -> path] """

    hash_path_map: dict[str, str] = {}
    videos_hashed, hashing_failed, collisions = [], [], []
    path_hash_map = { video_data.path: hash for hash, video_data in existing_videos.items() }
    for idx, video_path in enumerate(video_paths):
        print('\rFinding hashes for video paths ({:_}/{:_})'.format(idx+1, len(video_paths)), end='')
        video_hash: str|None = path_hash_map.get(video_path)
        # if video_hash is None: # get hash from metadata
        #     video_hash = _get_hash_from_video_metadata(video_path)
        if video_hash is None: # get filename embedded hash
            video_hash = _extract_filename_embedded_hash(video_path)
        if video_hash is None or rehash_videos:
            try:
                video_hash = video_analyser.getVideoHash_openCV(video_path)
                if video_hash is None:
                    hashing_failed.append(video_path)
                videos_hashed.append((video_hash, video_path))
            except Exception as e:
                LOGGER_HASHING_FAILED.error(e)
                hashing_failed.append(video_path)
            # if video_hash: # add hash to metadata
            #     _add_hash_to_video_metadata(video_path, video_hash)
            if video_hash: # update filename embedded hash
                try:
                    # _remove_filename_embedded_hash(video_path)
                    video_path = _update_filename_embedded_hash(video_path, video_hash)
                except (FileExistsError, PermissionError, OSError) as e:
                    hashing_failed.append(video_path)
                    LOGGER_HASHING_FAILED.error('Error when updating filename embedded hash for: "{}"\n error: {}'.format(video_path, e))
        if video_hash:
            if video_hash in hash_path_map:
                LOGGER_COLLISIONS.debug(f'hash [{video_hash}] shared by two videos:\n  1: {video_path}\n  2:{hash_path_map[video_hash]}')
                collisions.append(video_hash)
            else:
                hash_path_map[video_hash] = video_path
    # print hashing report
    print('\nDone. |  hashed: {:_}/{:_} videos  |  fails: {:_}  |  collisions: {:_}  |'.format(len(videos_hashed), len(video_paths), len(hashing_failed), len(collisions)))
    if videos_hashed != []:
        print('\n   VIDEOS HASHED:')
        for idx, (hsh, pth) in enumerate(videos_hashed):
            if idx > 5:
                print('...')
                break
            print('{:_} : [{}] "{}/{}"'.format(idx+1, hsh, Path(pth).parent.name, Path(pth).name))
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


#region - HELPERS ------------------------------------------------------------------------------------------------------

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


# VIDEO HASH FILENAME EMBEDDING

EMBEDDED_CPOPHASH_FORMAT =  r' #cpvhsh-{}'
EMBEDDED_CPOPHASH_PATTERN_EXTRACT = r' #cpvhsh-([0-9a-fA-F]+)[. ]'
EMBEDDED_CPOPHASH_PATTERN_REMOVE = r' #cpvhsh-([0-9a-fA-F]+)(?=[. ])' # wont consume the [. ] at the end
# ([0-9a-fA-F]+) - Captures 1+ hex digits (0-9, a-f, case insensitive) (+ means one or more of the preceding elements)
# [. ] - Matches either a period or space (end of tag)



def _extract_filename_embedded_hash(filepath: str) -> str|None:
    """ Extracts video hash embedded in filename """
    filename = os.path.basename(filepath)
    match = re.search(EMBEDDED_CPOPHASH_PATTERN_EXTRACT, filename)
    return match.group(1) if match else None


def _update_filename_embedded_hash(filepath: str, video_hash: str) -> str:
    """ Updates embeds hash into a files filename """
    filename = os.path.basename(filepath)
    filename_nohash = _remove_hash_from_filename(filename)
    new_filename = _add_hash_to_filename(filename_nohash, video_hash)
    if new_filename != filename:
        return rename_file(filepath, new_filename)
    return filepath


def _remove_filename_embedded_hash(filepath: str) -> str:
    """  """
    filename = os.path.basename(filepath)
    new_filename = _remove_hash_from_filename(filename)
    return rename_file(filepath, new_filename)


def _remove_hash_from_filename(filename: str):
    """ Removes hash embedded in video filename """
    return re.sub(EMBEDDED_CPOPHASH_PATTERN_REMOVE, '', filename).strip()


def _add_hash_to_filename(filename: str, video_hash: str) -> str:
    """ Adds hash to filename end. """
    base, ext = os.path.splitext(filename)
    hash_tag = EMBEDDED_CPOPHASH_FORMAT.format(video_hash)
    return f'{base}{hash_tag}{ext}'


def rename_file(old_path: str, new_name: str) -> str:
    dir_path = os.path.dirname(old_path)
    new_path = os.path.join(dir_path, new_name)
    os.rename(old_path, new_path)
    return new_path

