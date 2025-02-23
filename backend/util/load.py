""" Functions for the scanning and loading of files """
from typing import Any
import os
from pathlib import Path
import time
import yaml

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
]

# region #### PUBLIC #### 

# TODO: Remove with DB migration
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



def readFoldersAndCollections_YAML(filepath: str) -> tuple[list[str], list[str], dict]:
    """ Reads the list of colders and the collections they belong to from `video_folders.yaml """
    if not os.path.exists(filepath):
        raise FileNotFoundError("Collections file doesn't exist:", filepath)
    
    include_folders: list[str] = []
    ignore_folders: list[str] = []
    folder_collection: dict = {}

    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    for name, folders in data['collections'].items():
        if folders:
            ig_fol = [ convert_to_wsl_path(x) for x in folders if x.startswith('!') ]
            ignore_folders.extend(ig_fol)
            inc_fol = [ convert_to_wsl_path(x) for x in folders if x not in ig_fol ]
            include_folders.extend(inc_fol)
            for f in inc_fol:
                folder_collection[f] = name

    return include_folders, ignore_folders, folder_collection



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


# DEPRECATED!
def readFoldersAndCollections_YAML_TEXT(include_folders_file_path: str) -> tuple[list[str], list[str], dict]:
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

