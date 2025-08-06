""" Process videos (hashing, filename parsing, metadata getting, ...) """
import os
import time
from pathlib import Path
from dataclasses import fields

from handymatt import StringParser, json_metadata
from handymatt_media import video_analyser
from handymatt_media.metadata import video_metadata

from python_src.util.loggers import LOGGER_HASHING_FAILED, LOGGER_COLLISIONS, LOADING_FAILED
from python_src.util.general import extract_number_from_term
from python_src.schemas import VideoData
from .ntfs_ads import set_NTFS_ADS_tag, get_NTFS_ADS_tag


#region - PUBLIC -------------------------------------------------------------------------------------------------------

def process_videos(
    video_paths: list[str],
    existing_videos: dict[str, VideoData],
    collections_dict: dict[str, str],
    scene_filename_formats: list[str],
    rehash_videos = False,
    redo_video_attributes = False,
    reparse_filenames = False,
    reread_json_metadata = False,
) -> dict[str, VideoData]:
    """
    Given a list of video paths and a dictionary of previously scanned video data objects,
    find existing video data by filename, if needed, hash video, and process video. 
    Returns -> dict with all processed videos
    """
    
    videos_dict: dict[str, VideoData] = {}
    hash_path_map: dict[str, str] = _get_video_hashes(video_paths, existing_videos, rehash_videos=rehash_videos)
    # hash_path_map: dict[str, str] = _get_video_hashes_multi(video_paths, existing_videos, rehash_videos=rehash_videos) # multithreaded

    # process videos
    fails = []
    parser = StringParser(scene_filename_formats)
    for idx, (video_hash, video_path) in enumerate(hash_path_map.items()):
        print('\rprocessing videos ({:_}/{:_}) ({} fails) [{}] "{:<52}"'
            .format(idx+1, len(hash_path_map), len(fails), video_hash, _limit_and_filter_string(Path(video_path).name, 50)), end='')
        video_data: VideoData|None = existing_videos.get(video_hash)
        video_found_in_existing_videos = (video_data is not None)
        if not video_found_in_existing_videos or redo_video_attributes:
            video_data = _get_new_video_data_object(video_hash, video_path)

        if video_data is None:
            fails.append((video_hash, video_path))
        
        else:
            video_data.path = video_path                # update incase of path change
            video_data.filename = Path(video_path).name # update incase of path change
            video_data = _add_collection_attributes(video_data, collections_dict)

            if not video_found_in_existing_videos or reparse_filenames:
                # add data parsed from filename / path
                video_data = _add_filename_parsed_data(video_data, parser)
                # add extracted movie title and series
                
                video_data = _add_extracted_movie_series(video_data)
                # organize tags
                video_data = _get_tags_from_path(video_data)
                if video_data.title is None:
                    print('\nTITLE IS NONE: [{}] "{}"'.format(video_hash, video_path))
            
            if not video_found_in_existing_videos or reread_json_metadata:
                # get additional metadata from json files
                id_ = video_data.dvd_code or video_data.source_id or Path(video_data.path).stem
                if id_ is not None:
                    # from pprint import pprint
                    metadata = json_metadata.get_metadata(id_, video_data.path)
                    if metadata != {}:
                        video_data = _add_metadata_to_video_data(video_data, metadata)
                        video_data.actors = _get_ordered_set( video_data.primary_actors + video_data.secondary_actors )
            
            video_data.tags = list(set( video_data.tags_from_filename + video_data.tags_from_path + video_data.tags_from_json ))
            
            videos_dict[video_hash] = video_data
    print('\rprocessing videos ({:_}/{:_}) ({} fails) {:80}'
            .format(len(hash_path_map), len(hash_path_map), len(fails), 80*" "))
    
    # sort tags by occurance
    print("Sorting tags by frequencey ... ", end="")
    start = time.time()
    videos_dict = _sort_tags_by_frequency(videos_dict)
    print("Done! (took {:.2f}s)".format(time.time()-start))
    
    return videos_dict


# 
def combine_loaded_and_existing_videos(loaded: dict[str, VideoData], existing: dict[str, VideoData], unloaded_as_unlinked: bool=True) -> dict[str, VideoData]:
    """ Combines existing and loaded videos ensuring that videos that we're not loaded get flagged as not being linked """
    combined = {}
    for pid, obj in existing.items():
        if unloaded_as_unlinked:
            obj.is_linked = False
        combined[pid] = obj
    for pid, obj in loaded.items():
        obj.is_linked = True
        combined[pid] = obj
    return combined


#region - PRIVATE ------------------------------------------------------------------------------------------------------

def _get_video_hashes(
    video_paths: list[str],
    existing_videos: dict[str, VideoData],
    rehash_videos: bool=False,
) -> dict[str, str]:
    """ For a list of video paths, try to find their hash from exisiting videos, or else rehash. Return map[hash -> path] """

    hash_path_map: dict[str, str] = {}
    videos_hashed, hashing_failed, collisions, extracted_ads_tag, other_errors = [], [], [], [], []
    path_hash_map = { video_data.path: hash for hash, video_data in existing_videos.items() }
    for idx, video_path in enumerate(video_paths):
        # print('\rFinding hashes for video paths ({:_}/{:_})'.format(idx+1, len(video_paths)), end='')
        print('\rFinding hashes for video paths ({:_}/{:_})  "{:<52}"'.format(idx+1, len(video_paths), _limit_and_filter_string(Path(video_path).name, 50)), end='')
        video_hash: str|None = path_hash_map.get(video_path)
        if video_hash is None: # get NTFS ADS tag
            video_hash = get_NTFS_ADS_tag(video_path, 'candypop-video-hash')
            if video_hash:
                extracted_ads_tag.append(video_path)
        if video_hash is None or rehash_videos:
            try:
                video_hash = video_analyser.getVideoHash_openCV(video_path)
                # logging.info('Hashed video [{}] "{}"'.format(video_hash, video_path)) # Not working!
                if video_hash is None:
                    hashing_failed.append(video_path)
                videos_hashed.append((video_hash, video_path))
            except Exception as e:
                LOGGER_HASHING_FAILED.error(e)
                hashing_failed.append(video_path)
            if video_hash: # update NTFS ADS tag
                try:
                    set_NTFS_ADS_tag(video_path, 'candypop-video-hash', video_hash)
                except (FileExistsError, PermissionError, OSError) as e:
                    other_errors.append(video_path)
                    LOGGER_HASHING_FAILED.error('Error when updating filename embedded hash for: "{}"\n error: {}'.format(video_path, e))
        if video_hash:
            if video_hash in hash_path_map:
                LOGGER_COLLISIONS.debug(f'hash [{video_hash}] shared by two videos:\n  1: {video_path}\n  2: {hash_path_map[video_hash]}')
                collisions.append(video_hash)
            else:
                hash_path_map[video_hash] = video_path
    # print hashing report
    print("\rFinding hashes for video paths ({:_}/{:_}) {:<70}".format(len(video_paths), len(video_paths), 70*" "))
    print('All hashes found |  hashed: {:_}/{:_} videos  |  fails: {:_}  |  collisions: {:_}  |  ads_tags: {:_}  |  errors: {:_}'.format(len(videos_hashed), len(video_paths), len(hashing_failed), len(collisions), len(extracted_ads_tag), len(other_errors)))
    if videos_hashed != []:
        print('\n   VIDEOS HASHED:')
        for idx, (hsh, pth) in enumerate(videos_hashed):
            if idx > 5:
                print('...')
                break
            print('{:_} : [{}] "{}/{}"'.format(idx+1, hsh, Path(pth).parent.name, Path(pth).name[:120]))
    return hash_path_map



def _get_new_video_data_object(video_hash: str, video_path: str) -> VideoData|None:
    """ Get initial video data object. Add only hash, path, filename, and video attributes """
    
    extracted_data = {}
    try:
        extracted_data = video_analyser.getVideoData(video_path)
    except Exception as e:
        err_msg = '\nERROR: getVideoData() failed for [{}] \"{}\"\nmsg: {}'.format(video_hash, video_path, e)
        print(err_msg)
        LOADING_FAILED.error(err_msg)
        return None
    
    return VideoData(
        hash =          video_hash,
        path =          video_path,
        filename =      Path(video_path).name,
        date_added =    time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getctime(video_path))), # ctime
        duration =          extracted_data['duration'],
        duration_seconds =  extracted_data['duration_seconds'],
        filesize_mb =       extracted_data['filesize_mb'],
        fps =               extracted_data['fps'],
        resolution =        extracted_data['resolution'],
        bitrate =           extracted_data['bitrate'],
    )


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
    data.path_relative = str(Path(data.path).relative_to(Path(parent_dir))).replace('\\', '/')
    return data


""" 
TAGS:
    tags_from_path = [ p.replace('_', '') for p in path_relative.split(os.sep)[:-1] if p != '' ]
    obj['tags_from_path'] = [ t for t in tags_from_path if (t not in obj.get('performers', []) and t != obj.get('studio', '')) ]
    tags = obj.get('tags', [])
    tags.extend(obj['tags_from_path'])
    obj['tags'] = sorted(set(tags))
    
"""



def _add_filename_parsed_data(video_data: VideoData, parser: StringParser):
    """ Parse data from video filename, format slightly, and add to VideoData """

    path_obj = Path(video_data.path)
    filename_info_dict = _parse_filename(path_obj.stem, parser)
    if len(filename_info_dict) == 1:  # matched only title, using dirname as primary_actors
        fn = "{} - {}".format(path_obj.parent.name, path_obj.stem)
        filename_info_dict = _parse_filename(fn, parser)

    return _add_filename_info_to_scene_data(video_data, filename_info_dict)
    
    # video_data = _update_dataclass_from_dict(data, scene_info)



def _add_filename_info_to_scene_data(vd: VideoData, info: dict[str, str]):

    # scene attributes
    vd.title =    info.get('title')
    vd.studio =         info.get('studio')
    vd.line =           info.get('line')
    vd.dvd_code =       info.get('dvd_code')
    vd.source_id =      info.get('source_id')
    
    vd.primary_actors =    [ p for p in info.get('primary_actors', '').split(', ') if p != '' ]
    vd.secondary_actors = [ p for p in info.get('secondary_actors', '').split(', ') if p != '' ]
    vd.actors = _get_ordered_set( vd.primary_actors + vd.secondary_actors )

    # use year if no date_released
    date_released = None
    if 'date_released' in info:
        date_released = str(info['date_released'])
    elif 'date_released_alt' in info:
        date_released = str(info['date_released_alt'])
    elif 'year' in info:
        date_released = str(info['year'])
    vd.date_released = date_released
    
    vd.tags_from_filename = info.get('tags', []) # type: ignore
    
    return vd


def _get_tags_from_path(video_data: VideoData):
    """ Organize tags. Assumes all other attributes are in order. """
    if video_data.path_relative:
        parent_names = video_data.path_relative.replace(video_data.filename, '')
        tags_from_path = [ t.replace('_', '') for t in parent_names.split('/') if t != '' ]
        ignore_tags = video_data.actors + [ video_data.studio, video_data.line ]
        video_data.tags_from_path = [ t for t in tags_from_path if t not in ignore_tags ]
    
    return video_data


def _add_metadata_to_video_data(video_data: VideoData, metadata: dict) -> VideoData:
    
    metadata = _process_metadata(metadata)
    
    valid_keys = { field.name for field in video_data.__dataclass_fields__.values() }
    filtered_data = { k: v for k, v in metadata.items() if k in valid_keys }

    for k, v in filtered_data.items():
        if isinstance(v, list):
            l2 = getattr(video_data, k)
            for item in v:
                if item not in l2:
                    l2.append(item)
            setattr(video_data, k, l2)
        else:
            setattr(video_data, k, v) # TODO: Monitor for problems
        # elif not hasattr(video_data, k):
        #     setattr(video_data, k, v)

    return video_data



def _process_metadata(metadata: dict):

    # add artist to actors
    if "artist" in metadata:
        actors = metadata.get("primary_actors", [])
        actors.append(metadata["artist"])
        metadata["primary_actors"] = actors

    # add characters and source to tags
    tags = metadata.get("tags", [])
    characters = metadata.get("characters")
    if characters and isinstance(characters, list):
        tags.extend([ f"character: {c}" for c in characters ])
    
    sources = metadata.get("sources")
    if sources and isinstance(sources, list):
        tags.extend([ f"source: {c}" for c in sources ])

    # rename tags to tags_from_json
    if 'tags' in metadata:
        metadata['tags_from_json'] = metadata['tags']
        del metadata['tags']
    
    return metadata



def _parse_filename(filename: str, parser: StringParser):
    info = parser.parse(filename)
    if info is None:
        raise TypeError('String parser returned `None` for filename: "{}"'.format(filename))
    return info



def _sort_tags_by_frequency(videos_dict: dict[str, VideoData]) -> dict[str, VideoData]:
    """  """
    
    # get tag counts
    tag_counts = {}
    for vd in videos_dict.values():
        for tag in vd.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # sort
    special_tag_order = {
        "character": 99,
        "source": 98,
    }
    
    for vd in videos_dict.values():
        vd.tags = sorted(
            vd.tags,
            reverse=True,
            key=lambda tg: (
                special_tag_order.get(tg.split(": ")[0], 0) if (": " in tg) else -1,
                tag_counts[tg]
            ), # sortby tuple
        )

    return videos_dict



#region - GET MOVIE METHODS --------------------------------------------------------------------------------------------


def _add_extracted_movie_series(video_data: VideoData) -> VideoData:
    """  """
    title = video_data.title
    if title:
        movie, scene, scene_idx, series = _get_movie(title)
        if movie is not None:
            video_data.movie_title = movie
            video_data.scene_title = scene
            video_data.scene_number = scene_idx
            video_data.movie_series = series
    
    return video_data


def _get_movie(title):
    movie, scene, scene_idx, series = None, None, None, None
    
    words = title.lower().split(' ')
    
    for sc_delim in ['scene', 'part', 'episode', 'chapter']:
        if sc_delim in words:
            part_idx = words.index(sc_delim)
            if part_idx > 0 and len(words) > part_idx+1:
                part_word = _remove_chars(words[part_idx+1], ':;,꞉')
                scene_idx = extract_number_from_term(part_word)
                if scene_idx is not None:
                    movie, scene  = _extract_movie_and_scene_titles(title.split(' '), part_idx)
            break
    
    if movie is None and scene is None:
        delim = ' - '
        if delim in title:
            parts = title.split(delim)
            movie = delim.join(parts[:-1])
            scene = parts[-1]

    if movie:
        series = _get_movie_series_from_movie(movie)
    
    return movie, scene, scene_idx, series


def _extract_movie_and_scene_titles(words, delim_idx):
    scene = ' '.join(words[delim_idx:])
    movie = ' '.join(words[:delim_idx])
    if movie[-1] in ':;꞉':
        movie = movie[:-1]
    elif movie.endswith(' -'):
        movie = movie[:-2]
    return movie, scene

def _get_movie_series_from_movie(title):
    
    title_words = title.split(' ')
    title_words_lower = title.lower().split(' ')
    
    if len(title_words_lower) <= 1:
        return title
    
    for series_delim in ['vol', 'vol.', 'volume', 'season']:
        if series_delim in title_words_lower:
            part_idx = title_words_lower.index(series_delim)
            movie_series_parts = title_words[:part_idx]
            return ' '.join(movie_series_parts)
    
    movie_idx = extract_number_from_term(title_words_lower[-1])
    if movie_idx:
        return ' '.join(title_words[:-1])

    return title


def _remove_chars(string, chars):
    for c in chars:
        string = string.replace(c, '')
    return string



#region - MISC. HELPERS ------------------------------------------------------------------------------------------------

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


def _limit_and_filter_string(s: str, l: int) -> str:
    new = []
    count = 0
    for c in s:
        if ord(c) < 150:
            new.append(c)
            count += 1
        if count >= l:
            return "".join(new[:-3]) + "..."
    return "".join(new)