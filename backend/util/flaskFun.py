from typing import Any
import os
import time
from pathlib import Path
import pickle
import math
from scipy.sparse import csr_matrix, vstack



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


def parseFilenameJAV(fn):
    stem = Path(fn).stem
    parts = stem.split('[')
    actor = parts[0]
    title = stem[len(actor):]
    return actor.strip(), None, title


#### SIMILAR ITEMS ####


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

