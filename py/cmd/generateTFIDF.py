"""
Builds TF-IDF model from the video database and pickles it to disk.

Usage:
    python -m cmd.generateTFIDF --db-path <path/to/app.db> --model-dir <path/to/model/dir> [--build-profiles]

Outputs:
    <model-dir>/tdidf.pkl         - full TFIDFModel (vectorizer + matrix + id_index_map)
    <model-dir>/tdidf_matrix.pkl  - TFIDFModelMatrix (matrix + id_index_map, for fast lookup)

With --build-profiles also outputs:
    <model-dir>/actor_profiles.pkl   - TFIDFModelMatrix keyed by lowercased actor name
    <model-dir>/studio_profiles.pkl  - TFIDFModelMatrix keyed by lowercased studio name
"""
import argparse
import sys

from lib.util.db import read_videos_from_db
from lib.schemas.video_data import VideoData
from lib.recommender.tfidf import generate_tfidf_model, extract_model_matrix
from lib.util.general import pickle_save


def main(db_path: str, model_dir: str, build_profiles: bool = False):
    print(f'[TFIDF] Reading videos from: {db_path}')
    rows = read_videos_from_db(db_path)
    videos = [VideoData.from_dict(row, strict=False) for row in rows]
    print(f'[TFIDF] Building model for {len(videos):_} linked videos ...')

    model = generate_tfidf_model(videos)

    model_path = f'{model_dir}/tdidf.pkl'
    matrix_path = f'{model_dir}/tdidf_matrix.pkl'
    print(f'[TFIDF] Saving model to {model_path}')
    pickle_save(model, model_path)
    print(f'[TFIDF] Saving matrix to {matrix_path}')
    pickle_save(extract_model_matrix(model), matrix_path)

    if build_profiles:
        from lib.recommender.similarity import build_actor_profiles, build_studio_profiles

        print('[TFIDF] Building actor profiles ...')
        actor_matrix = build_actor_profiles(videos, model)
        actor_path = f'{model_dir}/actor_profiles.pkl'
        pickle_save(actor_matrix, actor_path)
        print(f'[TFIDF] Saved actor profiles to {actor_path}')

        print('[TFIDF] Building studio profiles ...')
        studio_matrix = build_studio_profiles(videos, model)
        studio_path = f'{model_dir}/studio_profiles.pkl'
        pickle_save(studio_matrix, studio_path)
        print(f'[TFIDF] Saved studio profiles to {studio_path}')

    print('[TFIDF] Done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', required=True, help='Path to app.db')
    parser.add_argument('--model-dir', required=True, help='Directory to write model pickle files')
    parser.add_argument('--build-profiles', action='store_true', help='Also build actor and studio item profiles')
    args = parser.parse_args()

    try:
        main(args.db_path, args.model_dir, args.build_profiles)
    except Exception as e:
        print(f'[TFIDF] ERROR: {e}', file=sys.stderr)
        sys.exit(1)
