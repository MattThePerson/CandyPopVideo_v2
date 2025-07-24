""" Functions for computing video, performer and studio similarity """
import math
from ..recommender import tfidf  # Weird import
from scipy.sparse import csr_matrix, vstack
from sklearn.feature_extraction.text import TfidfVectorizer

from src.schemas import TFIDFModel, VideoData

def get_similar_videos(video_hash: str, startfrom: int, limit: int, videos_list: list[VideoData], tfidf_model: TFIDFModel) -> tuple[list[VideoData], int]:
    sims = tfidf.get_similar_videos_for_hash_TFIDF(video_hash, tfidf_model)
    if sims is None or len(sims) == 0:
        return [], 0
    hash_sims = { hash: score for hash, score in sims }
    videos_list = [ vid for vid in videos_list if vid.hash in hash_sims ]
    videos_list.sort( reverse=True, key=lambda vid: hash_sims[vid.hash] )
    return videos_list[startfrom: startfrom+limit], len(videos_list)


def get_similar_performers(performer: str, embeddings_object: TFIDFModel) -> list[dict]:
    """ Given a performer and all performer embeddings, returns partial sorted list of most similar performers (by max embedding dot product) """
    embeddings_matrix, name_index_map = embeddings_object.matrix, embeddings_object.id_index_map
    perf_index = name_index_map.get(performer.lower())
    if perf_index is None:
        return []
    performer_embedding = embeddings_matrix[perf_index]
    # sims_items = get_similar_items_TFIDF(target_embedding, embeddings, name_index_map)
    sims_items = tfidf.get_similar_items_TFIDF_dot(performer_embedding, embeddings_matrix, name_index_map)
    results = [
        { 'name': name, 'sim': sim }
        for name, sim in sims_items[:100]
    ]
    return results


def generate_performer_embeddings_model(video_objects: list[dict], tfidf_model: TFIDFModel) -> TFIDFModel:
    """ Generate TFIDF model for performers based on weighted average of their video embeddings """
    performer_embeddings_matrix, performer_index_map = _generate_performer_embeddings(video_objects, tfidf_model.matrix, tfidf_model.id_index_map)
    return TFIDFModel(
        vectorizer =     TfidfVectorizer(), # doesnt do anything
        matrix =         performer_embeddings_matrix,
        id_index_map = performer_index_map,
    )


def _generate_performer_embeddings(video_objects: list[dict], tfidf_matrix: csr_matrix, hash_index_map: dict[str, int]) -> tuple[csr_matrix, dict[str, int]]:
    """ Generate embeddings (profiles) for performers from TF-IDF model """
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
def _get_mean_embedding_profiles_TFIDF(posessor_item_indices: dict[str, list], tfidf_matrix: csr_matrix) -> tuple[csr_matrix, dict[str, int]]:
    posessor_index_map = { perf: i for i, perf in enumerate(posessor_item_indices.keys()) }
    posessor_embeddings_array = []
    # video_count = { perf: len(indices) for perf, indices in posessor_item_indices.items() }
    embeddings_n = len(posessor_item_indices)
    for i, indices in enumerate(posessor_item_indices.values()):
        print('\rGenerating profile for ({}/{}) ({:.1f}%)'.format( i+1, embeddings_n, (i+1)/embeddings_n*100 ), end='')
        item_embeddings = vstack([ tfidf_matrix[idx] for idx in indices ])
        if item_embeddings.shape:
            embeddings_mean = csr_matrix(item_embeddings.mean(axis=0)) * (1 + math.log(item_embeddings.shape[0]))
            posessor_embeddings_array.append(embeddings_mean)
    print(' Done. Converting to vstack ...')
    posessor_embeddings: csr_matrix = vstack(posessor_embeddings_array) # type: ignore
    return posessor_embeddings, posessor_index_map
    # return posessor_embeddings, posessor_index_map, video_count


def newHashNotInTFIDF(video_hashes: list[str], hash_index_map: dict[str, str]) -> bool:
    """ Returns true if exists hash not in hash_index_map """
    for hash in video_hashes:
        if hash not in hash_index_map:
            return True
    return False

