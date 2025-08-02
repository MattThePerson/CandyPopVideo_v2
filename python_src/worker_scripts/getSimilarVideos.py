"""

"""


# video_hash, start_from, limit
def main(target_video_hash: str, start_from: int, limit: int):
    """  """
    
    import time
    start = time.time()
    from python_src.util import config, general
    from python_src.recommender.tfidf_light import get_similar_videos_for_hash_TFIDF
    from python_src.recommender.model_matrix import TFIDFModelMatrix

    import_tt = time.time() - start
    start = time.time()
    
    # load TF-IDF model
    tfidf_model: TFIDFModelMatrix|None = general.pickle_load(config.TFIDF_MODEL_MATRIX_PATH)
    if tfidf_model is None:
        raise Exception(f"Unable to pickle load TF-IDF model, possibly doesn't exist: '{config.TFIDF_MODEL_PATH}'")
    
    load_tt = time.time() - start
    start = time.time()
    
    # get similar items and return
    sims_items = get_similar_videos_for_hash_TFIDF(target_video_hash, tfidf_model)
    limit = 512
    hashes = [ x[0] for x in sims_items[:limit] ]
    sims =   [ x[1] for x in sims_items[:limit] ]

    compute_tt = time.time() - start
    
    return {
        "HashesList": hashes,
        "SimsList": sims,
        "Report": "import: {:.1f}ms  load: {:.1f}ms  compute: {:.1f}ms".format(import_tt*1000, load_tt*1000, compute_tt*1000),
    }





if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-target', type=str)
    parser.add_argument('-start_from', type=int)
    parser.add_argument('-limit', type=int)
    
    args = parser.parse_args()
    
    ret = main(args.target, args.start_from, args.limit)
    print(json.dumps(ret))
    