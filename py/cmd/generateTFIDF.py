"""
Builds TF-IDF model from the video database and pickles it to disk.

Usage:
    python -m cmd.generateTFIDF --db-path <path/to/app.db> --model-dir <path/to/model/dir>

Outputs two pickle files:
    <model-dir>/tdidf.pkl         - full TFIDFModel (vectorizer + matrix + id_index_map)
    <model-dir>/tdidf_matrix.pkl  - TFIDFModelMatrix (matrix + id_index_map, for fast lookup)
"""
import argparse
import sys

from lib.util.db import read_videos_from_db
from lib.schemas.video_data import VideoData
from lib.recommender.tfidf import generate_tfidf_model, extract_model_matrix
from lib.util.general import pickle_save


def main(db_path: str, model_dir: str):
    print(f'[TFIDF] Reading videos from: {db_path}')
    rows = read_videos_from_db(db_path)
    videos = [VideoData.from_dict(row, strict=False) for row in rows if row.get('is_linked')]
    print(f'[TFIDF] Building model for {len(videos):_} linked videos ...')

    model = generate_tfidf_model(videos)

    model_path = f'{model_dir}/tdidf.pkl'
    matrix_path = f'{model_dir}/tdidf_matrix.pkl'
    print(f'[TFIDF] Saving model to {model_path}')
    pickle_save(model, model_path)
    print(f'[TFIDF] Saving matrix to {matrix_path}')
    pickle_save(extract_model_matrix(model), matrix_path)
    print('[TFIDF] Done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', required=True, help='Path to app.db')
    parser.add_argument('--model-dir', required=True, help='Directory to write model pickle files')
    args = parser.parse_args()

    try:
        main(args.db_path, args.model_dir)
    except Exception as e:
        print(f'[TFIDF] ERROR: {e}', file=sys.stderr)
        sys.exit(1)
