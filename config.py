from handymatt.wsl_paths import convert_to_wsl_path

PREVIEW_MEDIA_DIR = convert_to_wsl_path(r'A:\WhisperaHQ\MyPrograms\MyApplications\CandyPopApp\Frontend\media')
CUSTOM_THUMBS_DIR = '...'
DB_PATH = 'data/app.db'
GIFS_DIR = convert_to_wsl_path(r'A:\Whispera\gifsFromCollection')

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
