import math

from scipy.sparse import csr_matrix, vstack
from sklearn.feature_extraction.text import TfidfVectorizer

from lib.recommender import tfidf
from lib.schemas.video_data import VideoData
from lib.recommender.tfidf_model import TFIDFModel


def generate_performer_embeddings_model(video_objects: list[dict], tfidf_model: TFIDFModel) -> TFIDFModel:
    perf_matrix, perf_index_map = _generate_performer_embeddings(video_objects, tfidf_model.matrix, tfidf_model.id_index_map)
    return TFIDFModel(
        vectorizer=TfidfVectorizer(),
        matrix=perf_matrix,
        id_index_map=perf_index_map,
    )


def get_similar_performers(performer: str, embeddings_object: TFIDFModel) -> list[dict]:
    embeddings_matrix, name_index_map = embeddings_object.matrix, embeddings_object.id_index_map
    perf_index = name_index_map.get(performer.lower())
    if perf_index is None:
        return []
    performer_embedding = embeddings_matrix[perf_index]
    sims_items = tfidf.get_similar_items_cosine(performer_embedding, embeddings_matrix, name_index_map)
    return [{'name': name, 'sim': sim} for name, sim in sims_items[:100]]


def get_similar_videos(video_hash: str, videos_list: list[VideoData], tfidf_model: TFIDFModel) -> list[VideoData]:
    sims = tfidf.get_similar_items_cosine(tfidf_model.matrix[tfidf_model.id_index_map[video_hash]], tfidf_model.matrix, tfidf_model.id_index_map)
    if not sims:
        return []
    hash_sims = {hash: score for hash, score in sims}
    result = [vid for vid in videos_list if vid.hash in hash_sims]
    result.sort(reverse=True, key=lambda vid: hash_sims[vid.hash])
    return result


def _generate_performer_embeddings(
    video_objects: list[dict],
    tfidf_matrix: csr_matrix,
    hash_index_map: dict[str, int],
) -> tuple[csr_matrix, dict[str, int]]:
    performer_videos_map: dict[str, list] = {}
    for vid in video_objects:
        performers = [p.lower() for p in set(vid.get('performers', [])) if p != '']
        for p in performers:
            indices = performer_videos_map.get(p, [])
            indices.append(hash_index_map[vid['hash']])
            performer_videos_map[p] = indices
    return _mean_embedding_profiles(performer_videos_map, tfidf_matrix)


def _mean_embedding_profiles(
    posessor_item_indices: dict[str, list],
    tfidf_matrix: csr_matrix,
) -> tuple[csr_matrix, dict[str, int]]:
    posessor_index_map = {perf: i for i, perf in enumerate(posessor_item_indices.keys())}
    posessor_embeddings_array = []
    n = len(posessor_item_indices)
    for i, indices in enumerate(posessor_item_indices.values()):
        print('\rGenerating profile ({}/{}) ({:.1f}%)'.format(i + 1, n, (i + 1) / n * 100), end='')
        item_embeddings = vstack([tfidf_matrix[idx] for idx in indices])
        embeddings_mean = csr_matrix(item_embeddings.mean(axis=0)) * (1 + math.log(item_embeddings.shape[0]))
        posessor_embeddings_array.append(embeddings_mean)
    print(' Done.')
    return vstack(posessor_embeddings_array), posessor_index_map  # type: ignore
