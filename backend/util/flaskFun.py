from typing import Any
import os
import time
from pathlib import Path
import random
from datetime import datetime
import pickle
import math

from scipy.sparse import csr_matrix, vstack

from handymatt import StringParser
from handymatt.wsl_paths import convert_to_wsl_path
from handymatt_media.video_analyser import video_analyser

import backend.util.backendFun as bf
from backend.util.metadata import metadata_load
from backend.util.search import *


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


# v 2.0
def getVideosInFolders(folders: list[str], ignore_folders=None):
    file_objects = []
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
    file_objects = [ obj for obj in file_objects if obj.suffix not in VIDEO_EXTENSIONS ]
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
                        existing_hash = video_analyser.getVideoHash(video_data.get('path')) # hash existing video to print
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


# TODO: REMOVE, DEPRICATED!
def processVideos_Old(video_paths, handler, collections_dict, scene_filename_formats):

    parser = StringParser(scene_filename_formats)
    
    videos_dict = {}
    hashing_failed, had_to_hash = [], []
    path_hash_map = { vd['path']: hash for hash, vd in handler.getItems() if 'path' in vd }

    collections_dict_paths = sorted(collections_dict.keys(), reverse=True, key=lambda path: len(path))

    for i, path in enumerate(video_paths):
        print("\r  Loading ({}/{}) {:<7}  {:<80}  ".format(i+1, len(video_paths), ("HASHING" if path not in path_hash_map else ""), f'"{path[:76]}"' ), end='')
        hash, extracted_data = None, {}
        if path in path_hash_map: # case 2
            path_in_db = True
            hash = path_hash_map[path]
        else: # case 1 or 3
            path_in_db = False
            had_to_hash.append(path)
            try:
                hash = video_analyser.getVideoHash(path)
                extracted_data = video_analyser.getVideoData(path)
                if hash == -1:
                    hashing_failed.append(path)
            except Exception as e:
                hashing_failed.append(path)
        
        if hash and hash != -1 and (path_in_db or extracted_data):
            new_entry = False
            obj = handler.getValue(hash)
            new_entry = obj==None
            if new_entry:
                obj = {}
                obj['hash'] = hash
            
            if not path_in_db: # case 1 or 3
                obj['path'] = path
            
            obj = add_collection_to_obj(obj, path, collections_dict, collections_dict_paths)
            obj = add_parsed_data_to_obj(obj, path, parser)
            if new_entry:
                for k, v in extracted_data.items():
                    obj[k] = v
            
            videos_dict[hash] = obj
            handler.setValue(hash, obj, nosave=True)
    handler.save()

    print("Tried to hash {} videos".format(len(had_to_hash)))
    if hashing_failed != []:
        print("\nFailed to hash {} videos:\n".format(len(hashing_failed)))
        for i, path in enumerate(hashing_failed):
            print("   {:>3} : '{}'".format(i+1, path[:80]))
        print()
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

#### SEARCH ####

# search, filter and sort videos
def searchVideosFunction(videos_dict, args, metadataHandler, tfidf_model, token_hashes):

    search_query, actor, studio, collection, include_terms, exclude_terms, date_added_from, date_added_to, date_released_from, date_released_to, only_favourites, sort_by = [ 
        args.get(x) for x in ['search', 'actor', 'studio', 'collection', 'include_terms', 'exclude_terms', 'date_added_from', 'date_added_to', 'date_released_from', 'date_released_to', 'only_favourites', 'sort_by']
    ]
    limit =     int( args.get('limit', 12) )
    startfrom = int( args.get('startfrom', 0) )
    favs = only_favourites == 'true'
    include_terms = [ x.lower().strip() for x in include_terms.split(',') ] if include_terms else []
    exclude_terms = [ x.lower().strip() for x in exclude_terms.split(',') ] if exclude_terms else []

    videos = list(videos_dict.values())
    videos.sort(reverse=True, key=lambda video: (
        video['date_added']
    ))
    
    # search videos
    if search_query:
        # videos = searchVideos_tokenHashes(videos, search_query, token_hashes)
        videos = searchVideos_TFIDF(videos, search_query, tfidf_model)
    
    # filter videos
    videos = filterVideos(videos, favs, actor, studio, collection, date_added_from, date_added_to, date_released_from, date_released_to, include_terms, exclude_terms, metadataHandler)
    if len(videos) < startfrom:
        return None

    # sort videos
    if sort_by and not search_query:
        videos = sortVideos(videos, sort_by)

    word_cloud = generate_word_cloud(videos, studio, actor, collection, include_terms)

    results_object = {
        'videos' : videos[startfrom: startfrom+limit],
        'amount_of_results' : len(videos),
        'word_cloud' : word_cloud
    }
    return results_object


# search videos DEPRECATED!
def searchVideos_tokenHashes(video_objects, search_query, token_hashes):
    print("\nFinding search results for query: '{}'".format(search_query))
    start = time.time()
    related_hashes, _ = get_related_hashes_from_query(token_hashes, search_query)
    print("  Done (took {}ms)".format(int((time.time()-start)*1_000)))
    hash_scores = { hash: score for hash, score in related_hashes }
    video_objects = [ vid for vid in video_objects if vid['hash'] in hash_scores ]
    video_objects.sort( reverse=True, key=lambda vid: hash_scores[vid['hash']] )
    return video_objects


# search videos TFIDF
def searchVideos_TFIDF(video_objects, search_query, tfidf_model):
    print("\n[TFIDF] Finding related videos for query: '{}'".format(search_query))
    start = time.time()
    # related_hashes, _ = get_related_hashes_from_query(token_hashes, search_query)
    related_hashes = get_related_videos_from_query_TFIDF(search_query, tfidf_model)
    print("  Done (took {}ms)".format(int((time.time()-start)*1_000)))
    hash_scores = { hash: score for hash, score in related_hashes if score > 0 }
    video_objects = [ vid for vid in video_objects if vid['hash'] in hash_scores ]
    video_objects.sort( reverse=True, key=lambda vid: hash_scores[vid['hash']] )
    return video_objects


# filter videos
def filterVideos(filtered, favs, actor, studio, collection, date_added_from, date_added_to, date_released_from, date_released_to, include_terms, exclude_terms, metadataHandler={}):
    
    if favs:            filtered = [ vid for vid in filtered if ( bf.is_favourite(vid['hash'], metadataHandler) ) ]
    if actor:           filtered = [ vid for vid in filtered if ( actor_in_video(actor, vid) ) ]
    if studio:          filtered = [ vid for vid in filtered if ( ( vid.get('studio') and studio.lower() in vid['studio'].lower() ) ) ]
    if collection:      filtered = [ vid for vid in filtered if ( (vid['collection'] and collection.lower() in vid['collection'].lower()) ) ]

    if date_added_from:     filtered = [ vid for vid in filtered if ( (get_video_date_released(vid) and get_video_date_released(vid) >= date_added_from) ) ]
    if date_added_to:       filtered = [ vid for vid in filtered if ( (get_video_date_released(vid) and get_video_date_released(vid) < date_added_to) ) ]
    if date_released_from:  filtered = [ vid for vid in filtered if ( (vid.get('date_released') and vid['date_released'] >= date_released_from) ) ]
    if date_released_to:    filtered = [ vid for vid in filtered if ( (vid.get('date_released') and vid['date_released'] < date_released_to) ) ]

    for term in include_terms:  filtered = [ vid for vid in filtered if ( term in vid['path'].lower() ) ]
    for term in exclude_terms:  filtered = [ vid for vid in filtered if ( term not in vid['path'].lower() ) ]

    return filtered


# sort videos
def sortVideos(videos, sort_by):
    videos.sort(
        reverse=False,
        key=lambda video: ( (video.get(sort_by) is None) != False, video.get('title', '') )
    )
    if sort_by == 'random':
        random.seed(str(datetime.now()))
        random.shuffle(videos)
    else:
        sort_reverse = ('desc' in sort_by)
        for x in ['-asc', '-desc']:
            sort_by = sort_by.replace(x, '')
        sort_by = sort_by.replace('-', '_')
        if sort_by == 'date_released':
            videos.sort(
                reverse=sort_reverse,
                key=lambda video: ( (video.get(sort_by) is None) != sort_reverse, get_video_date(video) ) # tuple where first element if boolean. 
            )
        else:
            videos.sort(
                reverse=sort_reverse,
                key=lambda video: ( (video.get(sort_by) is None) != sort_reverse, video.get(sort_by) ) # tuple where first element if boolean. 
            )
    return videos


# generate word cloud
def generate_word_cloud(videos, studio, actor, collection, include_terms, size_limit=20_000):
    word_cloud = []
    if len(videos) < size_limit:
        wc_exclude_terms = [ term.lower() for term in [studio, actor, collection] + include_terms if term != None ]
        word_cloud = get_word_cloud(videos, exclude_terms=wc_exclude_terms)
    return word_cloud


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

def get_video_date_released(vid):
    if 'date_released_d18':
        return vid['date_released_d18']
    return vid.get('date_released')

def actor_in_video(actor, vid):
        actor = actor.lower()
        performers_str = ''
        if 'performers' in vid and vid['performers'] != None:
            performers_str = ", ".join(vid['performers']).lower()
        mention_performers = ''
        if 'mention_performer' in vid and vid['mention_performer'] != None:
            mention_performers = vid['mention_performer'].lower()
        return actor in performers_str or actor in mention_performers


def limit_collections(folders_in, dict, filter):
    terms = filter.lower().split(' ')
    folders = []
    for f in folders_in:
        for term in terms:
            if dict[f].lower().startswith(term):
                folders.append(f)
                break
    return folders

def get_video_date(video):
    if 'date_released_d18' in video:
        return video['date_released_d18']
    return video['date_released']


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