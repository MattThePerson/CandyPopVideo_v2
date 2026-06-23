import numpy as np

from lib.recommender.model_matrix import TFIDFModelMatrix


def get_similar_videos_for_hash_TFIDF(video_hash: str, tfidf_model: TFIDFModelMatrix) -> list[tuple[str, float]]:
    matrix, hash_index_map = tfidf_model.matrix, tfidf_model.id_index_map
    video_index = hash_index_map.get(video_hash)
    if video_index is None:
        return []
    target_vector = matrix[video_index]
    return _get_similar_items(target_vector, matrix, hash_index_map)


def _get_similar_items(target_vect, matrix, id_index_map: dict[str, int]) -> list[tuple[str, float]]:
    index_id_map = {index: hash for hash, index in id_index_map.items()}
    cosine_sims = _cosine_similarity_sparse(target_vect, matrix)
    sims_items = [(idx, sim) for idx, sim in enumerate(cosine_sims)]
    sims_items.sort(reverse=True, key=lambda item: item[1])
    return [(index_id_map[idx], sim) for idx, sim in sims_items]


def _cosine_similarity_sparse(target, matrix) -> np.ndarray:
    dot_products = matrix.dot(target.T).toarray().flatten()
    target_norm = np.linalg.norm(target.data)
    matrix_norms = np.sqrt(matrix.multiply(matrix).sum(axis=1)).A.flatten()
    denom = matrix_norms * target_norm
    denom[denom == 0] = 1e-10
    return dot_products / denom
