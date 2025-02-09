import json
from handymatt.wsl_paths import convert_to_wsl_path

DB_PATH = 'data/app.db' # maybe include in settings.json?


SCENE_FILENAME_FORMATS = [
    '{sort_performers} - {studio:S} - [{year:d}];opt [{date_released:%Y-%m-%d}];opt [{line:S}];opt {scene_title} [{mention_performers:D}];opt {{{video_id:S}}};opt [id=={id:S}];opt',
    '[{studio:S}] [{year:d}];opt [{date_released:%Y-%m-%d}];opt [{line:S}];opt {scene_title} [{mention_performers:D}];opt',
    '{sort_performers} [{jave_code:S}] [{date_released:%Y-%m-%d}];opt [{studio:S}];opt {scene_title}',
    '[{jav_code:S}]',
    '{sort_performers} - {scene_title}',
    '{scene_title}',
]

# extensions to include as videos
VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.mov', '.avi', '.flv', '.wmv', '.vid', '.flv', '.webm']

# 
with open('data/settings.json', 'r') as f:
    settings = json.load(f)

# Mandatory fields
PREVIEW_MEDIA_DIR = convert_to_wsl_path(settings['preview_media_dir'])

# Optional fields
CUSTOM_THUMBS_DIR = convert_to_wsl_path(settings.get('custom_thumbs_dir'))
GIFS_DIR = convert_to_wsl_path(settings.get('gifs_dir'))

