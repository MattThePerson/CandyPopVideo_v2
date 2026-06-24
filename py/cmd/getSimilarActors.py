"""
Looks up similar actors for a target name using a pre-built actor profiles matrix.

Usage:
    python -m cmd.getSimilarActors --model-path <path/to/actor_profiles.pkl> --target "jane doe"

Output (JSON to stdout):
    {"NamesList": [...], "SimsList": [...], "Report": "import: Xms  load: Xms  compute: Xms"}
"""
import argparse
import json
import sys
import time


def main(model_path: str, target: str):
    t0 = time.time()

    from lib.util.general import pickle_load
    from lib.recommender.tfidf_light import get_similar_items_for_key
    from lib.recommender.model_matrix import TFIDFModelMatrix

    import_ms = (time.time() - t0) * 1000
    t1 = time.time()

    model: TFIDFModelMatrix | None = pickle_load(model_path)
    if model is None:
        print(json.dumps({"error": f"Model not found at: {model_path}"}))
        sys.exit(1)

    load_ms = (time.time() - t1) * 1000
    t2 = time.time()

    sims = get_similar_items_for_key(target.lower(), model)
    limit = 128
    names = [x[0] for x in sims[:limit]]
    scores = [x[1] for x in sims[:limit]]

    compute_ms = (time.time() - t2) * 1000

    print(json.dumps({
        "NamesList": names,
        "SimsList": scores,
        "Report": "import: {:.1f}ms  load: {:.1f}ms  compute: {:.1f}ms".format(import_ms, load_ms, compute_ms),
    }))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', required=True, help='Path to actor_profiles.pkl')
    parser.add_argument('--target', required=True, help='Target actor name')
    args = parser.parse_args()

    try:
        main(args.model_path, args.target)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
