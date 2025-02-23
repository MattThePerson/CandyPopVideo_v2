import yaml
from handymatt.wsl_paths import convert_to_wsl_path


# 
with open('yaml.config', 'r') as f:
    CONFIG = yaml.safe_load(f)

APP_DATA_DIR = convert_to_wsl_path(CONFIG['app_data_dir'])

CUSTOM_THUMBS_DIR = CONFIG.get('custom_thumbs_dir')
if CUSTOM_THUMBS_DIR:
    CUSTOM_THUMBS_DIR = convert_to_wsl_path(CUSTOM_THUMBS_DIR)

GIFS_DIR = CONFIG.get('gifs_dir')
if GIFS_DIR:
    GIFS_DIR = convert_to_wsl_path(GIFS_DIR)

SCENE_FILENAME_FORMATS = CONFIG.get('scene_filename_formats')
