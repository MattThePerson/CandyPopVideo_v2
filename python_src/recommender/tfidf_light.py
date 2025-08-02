import numpy as np
# from scipy.sparse import csr_matrix
# from sklearn.metrics.pairwise import cosine_similarity

from python_src.recommender.model_matrix import TFIDFModelMatrix


def get_similar_videos_for_hash_TFIDF(video_hash: str, tfidf_model: TFIDFModelMatrix) -> list[tuple[str, float]]:
    matrix, hash_index_map = tfidf_model.matrix, tfidf_model.id_index_map
    video_index = hash_index_map.get(video_hash)
    if video_index is None:
        return []
    target_vector = matrix[video_index]
    sims_items = get_similar_items_TFIDF(target_vector, matrix, hash_index_map)
    return sims_items


def get_similar_items_TFIDF(target_vect, matrix, id_index_map: dict[str, int]) -> list[tuple[str, float]]:
    index_id_map = { index: hash for hash, index in id_index_map.items() }
    # cosine_sims = cosine_similarity(target_vect, matrix)[0]
    cosine_sims = cosine_similarity_sparse(target_vect, matrix)
    sims_items = [ (idx, sim) for idx, sim in enumerate(cosine_sims) ]
    sims_items.sort(reverse=True, key=lambda item: item[1])
    sims_ids = [ (index_id_map[idx], sim) for idx, sim in sims_items ]
    return sims_ids



def cosine_similarity_sparse(target, matrix) -> np.ndarray:
    # Compute dot product between target and all rows in matrix
    dot_products = matrix.dot(target.T).toarray().flatten()
    
    # Compute norms
    target_norm = np.linalg.norm(target.data)
    matrix_norms = np.sqrt(matrix.multiply(matrix).sum(axis=1)).A.flatten()
    
    # Avoid division by zero
    denom = matrix_norms * target_norm
    denom[denom == 0] = 1e-10  # or handle differently if needed

    return dot_products / denom
