""" Functions for the scanning and loading of files """
from typing import Any
import os
from pathlib import Path
import time
import yaml

from handymatt.wsl_paths import convert_to_wsl_path

from config import SCENE_FILENAME_FORMATS, VIDEO_EXTENSIONS
from .metadata import metadata_load # TODO: outsource to handymatt dep
from .process import process_videos

# region #### PUBLIC #### 


def scanVideos() -> None:
    """ Scan videos in directories and process. Steps: read videos from db, scan videos, process videos, save to db """
    include_folders, ignore_folders, collections_dict = _readFoldersAndCollections_YAML('config.yaml')
    if include_folders == None:
        print("WARNING: No video folders read from config.yaml")
        return
    video_paths = _getVideoPathsFromFolders(include_folders, ignore_folders, include_extensions=VIDEO_EXTENSIONS)
    print("Found {} videos in {} folders from UNKNOWN collections".format(len(video_paths), len(include_folders)))
    
    print("Processing videos ...")
    start = time.time()
    existing_videos = {} # TODO: load from db
    videos_dict = process_videos(video_paths, existing_videos, collections_dict, SCENE_FILENAME_FORMATS)
    print("Successfully loaded {} videos (took {:.2f}s)\n".format(len(videos_dict), (time.time()-start)))





def _readFoldersAndCollections_YAML(filepath: str) -> tuple[list[str], list[str], dict]:
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



def _getVideoPathsFromFolders(folders: list[str], ignore_folders: list[str] = [], include_extensions: list[str] = []) -> list[str]:
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


