import os
import yaml
from handymatt.wsl_paths import convert_to_wsl_path


# 
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

# app data and subdirs
APP_DATA_DIR = convert_to_wsl_path(CONFIG['app_data_dir'])
PREVIEW_MEDIA_DIR = APP_DATA_DIR #os.path.join( APP_DATA_DIR, 'preview_media' )
CUSTOM_THUMBS_DIR = os.path.join( PREVIEW_MEDIA_DIR, 'custom_thumbs' )

GIFS_DIR = CONFIG.get('gifs_dir')
if GIFS_DIR:
    GIFS_DIR = convert_to_wsl_path(GIFS_DIR)

VIDEO_EXTENSIONS = CONFIG.get('video_extensions')

SCENE_FILENAME_FORMATS = CONFIG.get('scene_filename_formats')
