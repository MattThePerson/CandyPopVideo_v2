""" Functions for the scanning and loading of files """
from pathlib import Path
import time

from handymatt.wsl_paths import convert_to_wsl_path

from src.util import db
from src.util.config import SCENE_FILENAME_FORMATS, VIDEO_EXTENSIONS
from src.schemas import VideoData
from .process import process_videos, combine_loaded_and_existing_videos


#region main

def scanVideos(
        collections: dict[str, list],
        rehash_videos: bool=False,
        reparse_filenames: bool=False,
        redo_video_attributes: bool=False,
        reread_json_metadata: bool=False,
        path_filters: str|None=None,
        ws=None
        ) -> None:
    """ Scan videos in directories and process. Steps: read videos from db, scan videos, process videos, save to db """
    
    include_folders, ignore_folders, collections_dict = _process_collection_dirs(collections)
    if include_folders is None:
        print("WARNING: No video folders read from config.yaml")
        return
    print('[SCAN] Scanning video paths from {} folders'.format(len(include_folders)))
    video_paths = _getVideoPathsFromFolders(include_folders, ignore_folders, include_extensions=VIDEO_EXTENSIONS)
    print("Found {} videos in {} folders and {} collections".format(len(video_paths), len(include_folders), len(collections_dict)))
    
    # filter paths
    if path_filters:
        path_filters_list = [ f.lower().strip() for f in path_filters.split(',') ]
        print('Filtering video paths with filters:', path_filters_list)
        for fil in path_filters_list:
            video_paths = [ pth for pth in video_paths if fil in pth.lower() ]
        print('Left with {} videos'.format(len(video_paths)))
        
    # Load videos from db
    existing_dicts = db.read_table_as_dict('videos')
    existing_video_objects = { hsh: VideoData.from_dict(dct) for hsh, dct in existing_dicts.items() }
    print('Exising objects:', len(existing_video_objects))

    # 
    print("[PROCESS] Loading/Generating video objects")
    start = time.time()
    video_objects: dict[str, VideoData] = process_videos(video_paths, existing_video_objects, collections_dict, SCENE_FILENAME_FORMATS,
                                                            rehash_videos=rehash_videos, reparse_filenames=reparse_filenames,
                                                            redo_video_attributes=redo_video_attributes, reread_json_metadata=reread_json_metadata)
    if len(video_objects) > 0:
        print("Successfully loaded {} videos in {:.1f}s ({:.2f} ms/vid)\n".format( len(video_objects), (time.time()-start), (time.time()-start)*1000/len(video_objects) ))
    combined_video_objects = combine_loaded_and_existing_videos(video_objects, existing_video_objects, unloaded_as_unlinked=(path_filters is None))
    combined_video_dicts = { hsh: vd.to_dict()  for hsh, vd in combined_video_objects.items() }
    db.write_dict_of_objects_to_db(combined_video_dicts, 'videos')



#region helpers

def _process_collection_dirs(collections: dict[str, list]):
    include_folders: list[str] = []
    ignore_folders: list[str] = []
    folder_collection: dict = {}

    for name, folders in collections.items():
        if folders:
            inc_fol = [ x for x in folders if not x.startswith('!') ]
            ig_fol = [ x.replace('!','').strip() for x in folders if x not in inc_fol ]
            ignore_folders.extend(ig_fol)
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
    file_objects = [p for p in file_objects if not any(part.startswith('.') for part in p.parts[:-1])]
    video_paths = sorted(set([str(obj) for obj in file_objects]))
    return video_paths

