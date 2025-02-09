from typing import Any
import os
import time
from pathlib import Path
import pickle
import math
from scipy.sparse import csr_matrix, vstack

from handymatt import StringParser
from handymatt.wsl_paths import convert_to_wsl_path
from handymatt_media import video_analyser

from ..util.metadata import metadata_load
from ..search.tfidf import *


VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.mov', '.avi', '.flv', '.wmv', '.vid', '.flv', '.webm']


def readFoldersAndCollections(fn):
    if not os.path.exists(fn):
        print("ERROR: File doesn't exist, be sure to put folders into a file called: '{}'".format(fn))
        return [None]*3
    print("Reading collection folders from: '{}'".format(fn))
    with open(fn, 'r') as file:
        lines = [ line.strip() for line in file if (line != '\n' and not line.startswith('#')) ]
    
    include_folders, ignore_folders, collections_dict = [], [], {}
    current_collection = None
    for line in lines:
        if line ==  'END':
            break
        elif line.startswith('!'):
            ignore_folders.append(line[1:])
        elif ":" in line:
            include_folders.append(line)
            collections_dict[line] = current_collection
        else:
            current_collection = line
    return include_folders, ignore_folders, collections_dict


# 
def getVideosInFolders(folders: list[str], ignore_folders=None):
    file_objects: list[Path] = []
    if ignore_folders is None:
        ignore_folders = []
    ignore_folders.append('/.')
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
    file_objects = [ obj for obj in file_objects if obj.is_file() and obj.suffix in VIDEO_EXTENSIONS ]
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


#### PROCESS ####

# 
def processVideos(video_paths: list[str], handler, collections_dict, scene_filename_formats, reparse_filenames=False, show_collisions=False):
    
    parser = StringParser(scene_filename_formats)
    collections_dict_paths = sorted(collections_dict.keys(), reverse=True, key=lambda path: len(path))
    path_hash_map = { vd['path'].lower(): hash for hash, vd in handler.getItems() if 'path' in vd }
    
    hashing_failed, had_to_hash, collisions = [], [], []
    save_flag = True
    videos_dict = {}
    
    for i, path in enumerate(video_paths):
        path = convert_to_wsl_path(path)
        path_in_db = path.lower() in path_hash_map
        print("\r  Loading ({}/{}) (hashed:{} f:{}) {:<7}  {:<50}  "
            .format(i+1, len(video_paths), len(had_to_hash), len(hashing_failed), ("HASHING" if not path_in_db else ""), f'"{remove_nonascii_chars(Path(path).stem[:46])}"' ), end='')
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
                video_data = add_parsed_data_to_obj(video_data, path, parser)
                video_data = add_collection_to_obj(video_data, path, collections_dict, collections_dict_paths)
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



def add_collection_to_obj(obj, path, collections_dict, collections_dict_paths):
    parentdir = ''
    for dir in collections_dict_paths:
        if path.lower().startswith(dir.lower()):
            parentdir = dir
            break
    obj['collection'] = collections_dict.get(parentdir)
    obj['parentdir'] = parentdir
    obj['path_relative'] = path.lower().replace(parentdir.lower(), '')
    
    cut_fn = path.replace(parentdir, '')
    tags_from_path = [ p.replace('_', '') for p in cut_fn.split("\\")[:-1] if p != '' ]
    obj['tags_from_path'] = [ t for t in tags_from_path if (t not in obj.get('performers', []) and t != obj.get('studio', '')) ]
    tags = obj.get('tags', [])
    tags.extend(obj['tags_from_path'])
    obj['tags'] = sorted(set(tags))
    
    return obj

# 
def add_parsed_data_to_obj(obj, path, parser):
    path_obj = Path(path)
    obj['filename'] = path_obj.name
    scene_info = {}
    scene_info = parseFilenameForSceneInfo(path_obj.stem, parser)
    if len(scene_info) == 1:
        fn = "{} - {}".format(path_obj.parent.name, path_obj.stem)
        scene_info = parseFilenameForSceneInfo(fn, parser)
    
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


def getLinkedVideosFromJson(items):
    videos_dict = {}
    unlinked = []
    for i, (hash, obj) in enumerate(items):
        print('\r[LOAD] getting linked videos ({:_}/{:_}) ({:.1f}%) ({:_} unlinked)'
                .format(i+1, len(items), (i+1)/len(items)*100, len(unlinked)), end='')
        if os.path.exists(obj['path']):
            videos_dict[hash] = obj
        else:
            unlinked.append(obj)
    print()
    return videos_dict
    # videos_dict = { hash: obj for hash, obj in videosHandler.getItems() if os.path.exists(obj['path']) }


def parseFilenameForSceneInfo(fn, parser):
    info = parser.parse(fn)
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
    info['performers'] = get_ordered_set(performers)
    if 'scene_title' in info:
        info['title'] = info['scene_title']
        del info['scene_title']
    if 'year' not in info and 'line' in info and info['line'].replace('-','').isnumeric():
        info['date_released'] = info['line']
        info['year'] = info['line'][:4]
        del info['line']
    return info

# list of unique items which preserves order of original list
def get_ordered_set(arr):
    newarr = []
    seen = set()
    for item in arr:
        if item not in seen:
            newarr.append(item)
            seen.add(item)
    return newarr

def parseFilenameJAV(fn):
    stem = Path(fn).stem
    parts = stem.split('[')
    actor = parts[0]
    title = stem[len(actor):]
    return actor.strip(), None, title


#### SIMILAR ITEMS ####

# 
def get_similar_videos(hash, startfrom, limit, videos_dict, tfidf_model):
    sims = get_similar_videos_for_hash_TFIDF(hash, tfidf_model)
    if sims == None or len(sims) == 0:
        return None
    hash_sims = { hash: score for hash, score in sims }
    videos = [ vid for vid in videos_dict.values() if vid['hash'] in hash_sims ]
    videos.sort( reverse=True, key=lambda vid: hash_sims[vid['hash']] )
    results_object = {
        'videos' : videos[startfrom: startfrom+limit],
        'amount_of_results' : len(videos)
    }
    return results_object

def get_similar_performers(performer, embeddings_object):
    embeddings, name_index_map = embeddings_object['embeddings'], embeddings_object['name_index_map']
    perf_index = name_index_map.get(performer.lower())
    # print(performer)
    # print(perf_index)
    # print(embeddings.shape)
    if perf_index == None:
        return None
    target_embedding = embeddings[perf_index]
    # sims_items = get_similar_items_TFIDF(target_embedding, embeddings, name_index_map)
    sims_items = get_similar_items_TFIDF_dot(target_embedding, embeddings, name_index_map)
    results = [
        {'name': name, 'sim': sim, 'video_count': embeddings_object['video_count'][name.lower()]}
        for name, sim in sims_items[:100]
    ]
    return results


### MISC FUNCTIONS

def link_custom_thumbs(videos_dict, thumbs_dir):
    fn_to_hash = { vid['filename']: hash for hash, vid in videos_dict.items() }
    connected_suffix = 'CONN '
    unlinked_thumbs = [ t for t in os.listdir(thumbs_dir) if not t.startswith(connected_suffix) ]
    for i, thumb in enumerate(unlinked_thumbs):
        print('  ({}/{}) thumb: "{}"'.format(i+1, len(unlinked_thumbs), thumb))
        thumb_obj = Path(thumb)
        linked = False
        for fn in fn_to_hash.keys():
            if thumb_obj.stem.lower() in fn.lower():
                hash = fn_to_hash[fn]
                newname = '{}{} [{}]{}'.format(connected_suffix, thumb_obj.stem, hash, thumb_obj.suffix)
                old_path = os.path.join(thumbs_dir, thumb)
                new_path = os.path.join(thumbs_dir, newname)
                os.rename(old_path, new_path)
                videos_dict[hash]['custom_thumb'] = new_path
                print('Linked to video!\n:"{}"'.format(videos_dict[hash]['path']))
                linked = True
                break
        if not linked:
            print('Failed to link')
    return videos_dict


#### SMALL HELPER FUNCTIONS ####

def limit_collections(folders_in, dict, filter):
    terms = filter.lower().split(' ')
    folders = []
    for f in folders_in:
        for term in terms:
            if dict[f].lower().startswith(term):
                folders.append(f)
                break
    return folders

### 

def generate_tfidf_model(videos):

    tfidf, tfidf_matrix, hash_index_map = generate_tfidf_model_for_videos(videos)
    tfidf_model = {
        'model': tfidf, 'matrix': tfidf_matrix, 'hash_index_map': hash_index_map,
    }
    return tfidf_model

def generate_performer_embeddings(videos, tfidf_matrix, hash_index_map):
    PERFORMER_VIDEOS = {} # lists of indices
    for vid in videos:
        performers = vid.get('performers', []).copy()
        # mention_performers = vid.get('mention_performer', '').split(', ')
        # performers.extend(mention_performers)
        performers = [ p.lower() for p in set(performers) if p != '' ]
        for p in performers:
            video_indices = PERFORMER_VIDEOS.get(p, [])
            video_indices.append( hash_index_map[vid['hash']] )
            PERFORMER_VIDEOS[p] = video_indices
    return get_mean_embedding_profiles_TFIDF(PERFORMER_VIDEOS, tfidf_matrix)


# given a dict that defines groups of tfidf vectors, return profiles (mean embeddings)
def get_mean_embedding_profiles_TFIDF(posessor_item_indices, tfidf_matrix):
    posessor_index_map = { perf: i for i, perf in enumerate(posessor_item_indices.keys()) }
    posessor_embeddings = []
    video_count = { perf: len(indices) for perf, indices in posessor_item_indices.items() }
    embeddings_n = len(posessor_item_indices)
    for i, indices in enumerate(posessor_item_indices.values()):
        print('\rGenerating profile for ({}/{}) ({:.1f}%)'.format( i+1, embeddings_n, (i+1)/embeddings_n*100 ), end='')
        item_embeddings = vstack([ tfidf_matrix[idx] for idx in indices ])
        embeddings_mean = csr_matrix(item_embeddings.mean(axis=0)) * (1 + math.log(item_embeddings.shape[0])) # type: ignore
        posessor_embeddings.append(embeddings_mean)
    print(' Done. Converting to vstack ...')
    posessor_embeddings = vstack(posessor_embeddings)
    return posessor_embeddings, posessor_index_map, video_count


def newHashNotInTFIDF(video_hashes, hash_index_map):
    for hash in video_hashes:
        if hash not in hash_index_map:
            return True
    return False

def pickle_save(obj, fn):
    with open(fn, "wb") as f:
        pickle.dump(obj, f)

def pickle_load(fn):
    if not os.path.exists(fn):
        return None
    with open(fn, "rb") as f:
        obj = pickle.load(f)
    return obj

def remove_nonascii_chars(string):
    ch = []
    for c in string:
        if ord(c) < 256:
            ch.append(c)
    return ''.join(ch)