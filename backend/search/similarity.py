""" Functions for computing video, performer and studio similarity """
import math
from ..search import tfidf  # Weird import
from scipy.sparse import csr_matrix, vstack


def get_similar_videos(video_hash: str, startfrom: int, limit: int, videos_dict: dict[str, dict], tfidf_model) -> dict | None:
    sims = tfidf.get_similar_videos_for_hash_TFIDF(hash, tfidf_model)
    if sims is None or len(sims) == 0:
        return None
    hash_sims = { hash: score for hash, score in sims }
    videos = [ vid for vid in videos_dict.values() if vid['hash'] in hash_sims ]
    videos.sort( reverse=True, key=lambda vid: hash_sims[vid['hash']] )
    results_object = {
        'videos' : videos[startfrom: startfrom+limit],
        'amount_of_results' : len(videos)
    }
    return results_object


def get_similar_performers(performer: str, embeddings_object: dict) -> list[dict] | None:
    """ Given a performer and all performer embeddings, returns partial sorted list of most similar performers (by max embedding dot product) """
    embeddings, name_index_map = embeddings_object['embeddings'], embeddings_object['name_index_map']
    perf_index = name_index_map.get(performer.lower())
    if perf_index is None:
        return None
    target_embedding = embeddings[perf_index]
    # sims_items = get_similar_items_TFIDF(target_embedding, embeddings, name_index_map)
    sims_items = tfidf.get_similar_items_TFIDF_dot(target_embedding, embeddings, name_index_map)
    results = [
        {'name': name, 'sim': sim, 'video_count': embeddings_object['video_count'][name.lower()]}
        for name, sim in sims_items[:100]
    ]
    return results



def generate_performer_embeddings(video_objects: list[dict], tfidf_matrix: csr_matrix, hash_index_map: dict[str, int]):
    """ Generate embeddings (profiles) for performers based on """
    performer_videos_map: dict[str, list] = {} # lists of indices
    for vid in video_objects:
        performers = vid.get('performers', []).copy()
        # mention_performers = vid.get('mention_performer', '').split(', ')
        # performers.extend(mention_performers)
        performers = [ p.lower() for p in set(performers) if p != '' ]
        for p in performers:
            video_indices = performer_videos_map.get(p, [])
            video_indices.append( hash_index_map[vid['hash']] )
            performer_videos_map[p] = video_indices
    return _get_mean_embedding_profiles_TFIDF(performer_videos_map, tfidf_matrix)


# given a dict that defines groups of tfidf vectors, return profiles (mean embeddings)
def _get_mean_embedding_profiles_TFIDF(posessor_item_indices: dict[str, list], tfidf_matrix: csr_matrix):
    posessor_index_map = { perf: i for i, perf in enumerate(posessor_item_indices.keys()) }
    posessor_embeddings = []
    video_count = { perf: len(indices) for perf, indices in posessor_item_indices.items() }
    embeddings_n = len(posessor_item_indices)
    for i, indices in enumerate(posessor_item_indices.values()):
        print('\rGenerating profile for ({}/{}) ({:.1f}%)'.format( i+1, embeddings_n, (i+1)/embeddings_n*100 ), end='')
        item_embeddings = vstack([ tfidf_matrix[idx] for idx in indices ])
        if item_embeddings.shape:
            embeddings_mean = csr_matrix(item_embeddings.mean(axis=0)) * (1 + math.log(item_embeddings.shape[0]))
            posessor_embeddings.append(embeddings_mean)
    print(' Done. Converting to vstack ...')
    posessor_embeddings = vstack(posessor_embeddings)
    return posessor_embeddings, posessor_index_map, video_count


def newHashNotInTFIDF(video_hashes: list[str], hash_index_map: dict[str, str]) -> bool:
    """ Returns true if exists hash not in hash_index_map """
    for hash in video_hashes:
        if hash not in hash_index_map:
            return True
    return False

