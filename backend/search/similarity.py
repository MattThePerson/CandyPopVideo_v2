""" Functions for computing video, performer and studio similarity """

from .tfidf import *


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
