import math

from scipy.sparse import csr_matrix, vstack

from lib.recommender.tfidf_model import TFIDFModel
from lib.recommender.model_matrix import TFIDFModelMatrix
from lib.schemas.video_data import VideoData


def build_actor_profiles(videos: list[VideoData], model: TFIDFModel) -> TFIDFModelMatrix:
    item_indices: dict[str, list[int]] = {}
    for vid in videos:
        for name in (vid.actors or []):
            key = name.lower().strip()
            if not key or vid.hash not in model.id_index_map:
                continue
            item_indices.setdefault(key, []).append(model.id_index_map[vid.hash])
    return _build_item_profiles(item_indices, model.matrix)


def build_studio_profiles(videos: list[VideoData], model: TFIDFModel) -> TFIDFModelMatrix:
    item_indices: dict[str, list[int]] = {}
    for vid in videos:
        key = (vid.studio or '').lower().strip()
        if not key or vid.hash not in model.id_index_map:
            continue
        item_indices.setdefault(key, []).append(model.id_index_map[vid.hash])
    return _build_item_profiles(item_indices, model.matrix)


def _build_item_profiles(
    item_indices: dict[str, list[int]],
    tfidf_matrix: csr_matrix,
) -> TFIDFModelMatrix:
    index_map = {name: i for i, name in enumerate(item_indices.keys())}
    embeddings = []
    n_total = len(item_indices)
    for i, (name, indices) in enumerate(item_indices.items()):
        print(f'\rGenerating profile ({i+1}/{n_total}) ({(i+1)/n_total*100:.1f}%)', end='')
        vecs = vstack([tfidf_matrix[idx] for idx in indices])
        profile = csr_matrix(vecs.mean(axis=0)) * (1 + math.log(len(indices)))
        embeddings.append(profile)
    print(' Done.')
    return TFIDFModelMatrix(matrix=vstack(embeddings), id_index_map=index_map)
