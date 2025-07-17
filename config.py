import os
import yaml

from handymatt.wsl_paths import convert_to_wsl_path


with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)


# APP DATA
APP_DATA_DIR = convert_to_wsl_path(CONFIG.get('app_data_dir'))
DB_PATH =           APP_DATA_DIR + '/app.db'
TFIDF_MODEL_PATH =  APP_DATA_DIR + '/tdidf.pkl'
PREVIEW_MEDIA_DIR = APP_DATA_DIR + '/media/preview'
ACTOR_INFO_DIR = APP_DATA_DIR + '/actors'
# CUSTOM_THUMBS_DIR = APP_DATA_DIR + '/media/custom_thumbs'
os.makedirs(APP_DATA_DIR, exist_ok=True)

# GIFS
GIFS_DIR = CONFIG.get('gifs_dir')
if GIFS_DIR:
    GIFS_DIR = convert_to_wsl_path(GIFS_DIR)

VIDEO_EXTENSIONS = CONFIG.get('video_extensions')

SCENE_FILENAME_FORMATS = CONFIG.get('scene_filename_formats')

COLLECTIONS = CONFIG.get('collections')

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

SUBTITLE_FOLDERS = CONFIG.get('subtitle_folders')
