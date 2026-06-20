import os
import yaml

from handymatt.wsl_paths import convert_to_wsl_path


with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)


# APP DATA
APP_DATA_DIR = convert_to_wsl_path(CONFIG.get('app_data_dir'))
if APP_DATA_DIR:
    DB_PATH                  = APP_DATA_DIR + '/app.db'
    TFIDF_MODEL_PATH         = APP_DATA_DIR + '/tdidf.pkl'
    TFIDF_MODEL_MATRIX_PATH  = APP_DATA_DIR + '/tdidf_matrix.pkl'
    PREVIEW_MEDIA_DIR        = APP_DATA_DIR + '/media/preview'
    ACTOR_INFO_DIR           = APP_DATA_DIR + '/actors'
    os.makedirs(APP_DATA_DIR, exist_ok=True)
else:
    DB_PATH = TFIDF_MODEL_PATH = TFIDF_MODEL_MATRIX_PATH = PREVIEW_MEDIA_DIR = ACTOR_INFO_DIR = None

# GIFS
# GIFS_DIR = CONFIG.get('gifs_dir')
# if GIFS_DIR:
#     GIFS_DIR = convert_to_wsl_path(GIFS_DIR)

VIDEO_EXTENSIONS = CONFIG.get('video_extensions')

SCENE_FILENAME_FORMATS = CONFIG.get('scene_filename_formats')

COLLECTIONS = CONFIG.get('collections')

DATETIME_FORMAT = CONFIG.get('datetime_format')

SUBTITLE_FOLDERS = CONFIG.get('subtitle_folders')
