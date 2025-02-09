""" Functions for the scanning and processing of files """
from typing import Any
import os
from pathlib import Path
import time

from handymatt import StringParser
from handymatt.wsl_paths import convert_to_wsl_path
from handymatt_media import video_analyser

# from ..search import tfidf

from .metadata import metadata_load # TODO: outsource to handymatt dep

__all__ = [
    'readFoldersAndCollections',
    'getVideosInFolders',
    'getPerformers',
    'getStudios',
    'processVideos',
]

# region #### PUBLIC #### 

# TODO: Replace
def getLinkedVideosFromJson(existing_videos_dict: dict) -> dict[str, dict]:
    """ From the existing `videos.json` file, return those video objects that are linked (path exists) """
    videos_dict = {}
    unlinked = []
    for i, (hash, obj) in enumerate(existing_videos_dict.items()):
        print('\r[LOAD] getting linked videos ({:_}/{:_}) ({:.1f}%) ({:_} unlinked)'
                .format(i+1, len(existing_videos_dict), (i+1)/len(existing_videos_dict)*100, len(unlinked)), end='')
        if os.path.exists(obj['path']):
            videos_dict[hash] = obj
        else:
            unlinked.append(obj)
    print()
    return videos_dict
    # videos_dict = { hash: obj for hash, obj in videosHandler.getItems() if os.path.exists(obj['path']) }


# DEPRECATED!
def readFoldersAndCollections(include_folders_file_path: str) -> tuple[list[str], list[str], dict]:
    """ DEPRECATED!!! Reads the list of colders and the collections they belong to from `video_folders.yaml` """
    if not os.path.exists(include_folders_file_path):
        raise FileNotFoundError("File doesnt exist")
    with open(include_folders_file_path, 'r') as file:
        lines = [ line.strip() for line in file if (line != '\n' and not line.startswith('#')) ]
    include_folders: list[str] = []
    ignore_folders: list[str] = []
    collections_dict: dict = {}
    current_collection = 'No Collection'
    for line in lines:
        if line == 'END':
            break
        elif line.startswith('!'):
            ignore_folders.append(line[1:])
        elif ":" in line:
            include_folders.append(line)
            dirpath = convert_to_wsl_path(line)
            collections_dict[dirpath] = current_collection
        else:
            current_collection = line
    return include_folders, ignore_folders, collections_dict


def readFoldersAndCollections_YAML(include_folders_file_path: str) -> tuple[list[str], list[str], dict]:
    """ Reads the list of colders and the collections they belong to from `video_folders.yaml` """
    if not os.path.exists(include_folders_file_path):
        raise FileNotFoundError("File doesnt exist")
    with open(include_folders_file_path, 'r') as file:
        lines = [ line.strip() for line in file if (line != '\n' and not line.strip().startswith('#')) ]
    include_folders: list[str] = []
    ignore_folders: list[str] = []
    collections_dict: dict = {}
    current_collection = 'No Collection'
    for line in lines:
        if line == 'END: HERE':
            break
        if line.endswith(':'):
            current_collection = line
        else:
            folder_path = line
            folder_path = convert_to_wsl_path(folder_path)
            if line.startswith('!'):
                ignore_folders.append(folder_path)
            else:
                include_folders.append(folder_path)
                collections_dict[folder_path] = current_collection
    return include_folders, ignore_folders, collections_dict


def getVideosInFolders(folders: list[str], ignore_folders: list[str] = [], include_extensions: list[str] = []) -> list[str]:
    """ Given a list of folder and exclude folders (abspath or folder name) returns """
    file_objects: list[Path] = []
    ignore_folders.append('/.') # exclude all hidden folders
    folders =           [ convert_to_wsl_path(pth) for pth in folders ]
    ignore_folders =    [ convert_to_wsl_path(pth) for pth in ignore_folders ]
    # fetch files
    start = time.time()
    for idx, base_folder in enumerate(sorted(folders)):
        print('\rScanning files in folders ({}/{}) files: {:_}'.format(idx, len(folders), len(file_objects)), end='')
        file_objects.extend(list(Path(base_folder).rglob('*')))
    print('\rScanning files ({:_}) from folders ({}/{})'.format(len(file_objects), len(folders), len(folders)), end='')
    print(' took {:.1f} seconds'.format(time.time()-start))
    # filter files
    file_objects = [ obj for obj in file_objects if obj.is_file() and obj.suffix in include_extensions ]
    for igfol in ignore_folders:
        file_objects = [ obj for obj in file_objects if igfol not in str(obj) ]
    video_paths = sorted(set([str(obj) for obj in file_objects]))
    return video_paths


def getPerformers(videos_dict):
    d = {}
    for vid in videos_dict.values():
        for p in vid.get('performers', []):
            d[p] = d.get(p, 0) + 1
    if '' in d:
        del d['']
    return d


def getStudios(videos_dict):
    d = {}
    for vid in videos_dict.values():
        k = vid.get('studio')
        if k:
            d[k] = d.get(k, 0) + 1
    return d


# TODO: Decouple from JsonHandler
def processVideos(video_paths: list[str], handler, collections_dict: dict[str, str], scene_filename_formats: list[str], reparse_filenames=False, show_collisions=False) -> dict[str, dict]:
    """ Given a list of video paths """
    parser = StringParser(scene_filename_formats)
    path_hash_map = { vd['path'].lower(): hash for hash, vd in handler.getItems() if 'path' in vd }
    
    hashing_failed, had_to_hash, collisions = [], [], []
    save_flag = True
    videos_dict: dict[str, dict] = {}
    
    for i, path in enumerate(video_paths):
        path = convert_to_wsl_path(path)
        path_in_db = path.lower() in path_hash_map
        print("\r  Loading ({}/{}) (hashed:{} f:{}) {:<7}  {:<50}  "
            .format(i+1, len(video_paths), len(had_to_hash), len(hashing_failed), ("HASHING" if not path_in_db else ""), f'"{_remove_nonascii_chars(Path(path).stem[:46])}"' ), end='')
        # Check if path in DB
        if path_in_db:
            hash = path_hash_map[path.lower()]
        else:
            try:
                hash = video_analyser.getVideoHash(path) # can return -1
                had_to_hash.append((path, hash))
            except Exception as e:
                hash = -1
                print('\nEXCEPTION')
                print(os.path.exists(path))
                print(os.path.isfile(path))
                print(e)
                exit(1)
        # Add data if hash exists
        if hash == -1:
            hashing_failed.append(path)
        else:
            video_data: dict[str, Any] = handler.getValue(hash)
            if not video_data: # New entry
                video_data = {'hash': hash}
                extracted_data = video_analyser.getVideoData(path)
                for k, v in extracted_data.items():
                    video_data[k] = v
            elif not path_in_db:
                if os.path.exists(video_data.get('path', '')): # if video exists with same hash
                    collisions.append(hash)
                    if show_collisions:
                        existing_hash = video_analyser.getVideoHash(video_data.get('path', '')) # hash existing video to print
                        print('\nFound entry with same has that exists')
                        print('HASH1: [{}]  HASH2: [{}]'.format(hash, existing_hash))
                        print('EXISTING PATH: "{}"'.format(video_data.get('path')))
                        print('REPLACE PATH:  "{}"\n'.format(path))
            if reparse_filenames or not path_in_db: # path changed, re-parse filename
                video_data['path'] = path
                video_data['tags'] = []
                video_data = _add_parsed_data_to_obj(video_data, path, parser)
                video_data = _add_collection_to_obj(video_data, collections_dict)
                video_id = video_data.get('id')
                if video_id:
                    metadata = metadata_load(path, video_id)
                    if metadata:
                        video_data['metadata'] = metadata
                        for key in ['tags', 'stars']:
                            for tag in metadata.get(key, []):
                                video_data['tags'].append(tag)
            videos_dict[hash] = video_data
            handler.setValue(hash, video_data, nosave=True)
            if (len(had_to_hash)+1)%50 == 0:
                # print('\nSAVING ...')
                if save_flag:
                    handler.save()
                    save_flag = False
            else:
                save_flag = True
    handler.save()

    print("\nTried to hash {} videos ({} collisions):".format(len(had_to_hash), len(collisions)))
    for i, (path, hash) in enumerate(had_to_hash[:10]):
        print('   {:>3} : [{}] "{}/{}"'.format(i+1, hash, Path(path).parent.name, Path(path).name[:90]))
    if hashing_failed != []:
        print("\nFailed to hash {} videos:\n".format(len(hashing_failed)))
        for i, path in enumerate(hashing_failed):
            print("   {:>3} : '{}'".format(i+1, path[:100]))
    return videos_dict


# region #### PRIVATE #### 

def _add_collection_to_obj(obj: dict, collections_dict: dict) -> dict:
    """ Given a video object, determine its collection and add collection and split up paths (parents & relative path) """
    video_path = obj['path']
    parentdir = None
    collections_dict_paths = sorted(collections_dict.keys(), reverse=True, key=lambda path: len(path))
    for dir in collections_dict_paths:
        if video_path.startswith(dir):
            parentdir = dir
            break
    collection = collections_dict.get(parentdir)
    if collection is None or parentdir is None:
        raise KeyError('Collection not defined for parentdir: "{}"'.format(parentdir))
    obj['collection'] = collection
    obj['parentdir'] = parentdir
    path_relative = str(Path(video_path).relative_to(Path(parentdir)))
    obj['path_relative'] = path_relative
    
    tags_from_path = [ p.replace('_', '') for p in path_relative.split(os.sep)[:-1] if p != '' ]
    obj['tags_from_path'] = [ t for t in tags_from_path if (t not in obj.get('performers', []) and t != obj.get('studio', '')) ]
    tags = obj.get('tags', [])
    tags.extend(obj['tags_from_path'])
    obj['tags'] = sorted(set(tags))
    
    return obj

# 
def _add_parsed_data_to_obj(obj, path, parser):
    path_obj = Path(path)
    obj['filename'] = path_obj.name
    scene_info = {}
    scene_info = _parseFilenameForSceneInfo(path_obj.stem, parser)
    if len(scene_info) == 1:
        fn = "{} - {}".format(path_obj.parent.name, path_obj.stem)
        scene_info = _parseFilenameForSceneInfo(fn, parser)
    
    if 'date_released' not in scene_info or scene_info['date_released'] == None:
        scene_info['date_released'] = str(scene_info.get('year')) if scene_info.get('year') else None
    else:
        scene_info['date_released'] = str(scene_info['date_released'])
    
    # delete previous scene info
    for k in ['mention_performer', 'line', 'other_info', 'year', 'studio', 'jav_code']:
        if k in obj:
            del obj[k]
    obj['actor'] = ''
    
    if 'tags' in scene_info:
        obj['tags_from_filename'] = scene_info['tags']
        del scene_info['tags']
    
    for k, v in scene_info.items():
        obj[k] = v

    obj['date_added'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getctime(path)))
    
    tags = obj.get('tags', [])
    tags.extend(obj.get('tags_from_filename', []))
    obj['tags'] = sorted(set(tags))
    
    return obj



def _parseFilenameForSceneInfo(filename: str, parser: StringParser):
    info = parser.parse(filename)
    if info is None:
        raise TypeError('String parser returned `None` for filename: "{}"'.format(filename))
    performers = []
    if 'sort_performers' in info:
        info['actor'] = info['sort_performers']
        performers += info['sort_performers'].split(", ")
        # del info['sort_performers']
    if 'mention_performers' in info:
        if info['mention_performers'].islower():
            if 'scene_id' not in info:
                info['scene_id'] = info['mention_performers']
            else:
                info['scene_title'] += ' [{}]'.format(info['mention_performers'])
            del info['mention_performers']
        else:
            performers += info['mention_performers'].split(', ')
    info['performers'] = _get_ordered_set(performers)
    if 'scene_title' in info:
        info['title'] = info['scene_title']
        del info['scene_title']
    if 'year' not in info and 'line' in info and info['line'].replace('-','').isnumeric():
        info['date_released'] = info['line']
        info['year'] = info['line'][:4]
        del info['line']
    return info



# region #### HELPERS #### 

# list of unique items which preserves order of original list
def _get_ordered_set(arr):
    newarr = []
    seen = set()
    for item in arr:
        if item not in seen:
            newarr.append(item)
            seen.add(item)
    return newarr

def _remove_nonascii_chars(string):
    ch = []
    for c in string:
        if ord(c) < 256:
            ch.append(c)
    return ''.join(ch)
