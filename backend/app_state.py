from typing import Any
import os
import time
import threading

from handymatt import JsonHandler

from config import VIDEO_EXTENSIONS
from .util import process
from .search import tfidf

from .util import flaskFun as ff # TODO: remove dep


### 

class AppState:
    """ Thread-safe singleton class to manage app state. """

    MEDIADIR = "frontend/media/videos" # TODO: REMOVE AFTER REFACTOR
    CUSTOM_THUMBS_DIR = "frontend/media/custom_thumbs" # TODO: REMOVE AFTER REFACTOR

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AppState, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return  # Prevent re-initialization
        self._initialized = True

        self.videosHandler: JsonHandler | None = None
        self.metadataHandler: JsonHandler | None = None
        self.settingsHandler: JsonHandler | None = None

        self.videos_dict: dict[str, Any] = {}

        self.tfidf_model = None
        self.performer_embeddings = None

    # region LOAD
    
    def load(self,
            data_dir: str,
            reparse_filenames: bool = False,
            quick_start: bool = False,
            regen_tfidf_profiles: bool = False,
            recalculate_performer_embeddings: bool = False,
            purge_unloaded_video_objects: bool = False,
            backup_videos_handler: bool = False,
    ):
        # if not os.path.exists(DATADIR):
        #     os.mkdir(DATADIR)
        self.videosHandler =     JsonHandler( os.path.join( data_dir, 'videos.json' ), prettify=True)
        self.metadataHandler =   JsonHandler( os.path.join( data_dir, 'metadata.json' ))
        self.settingsHandler =   JsonHandler( os.path.join( data_dir, 'settings.json' ))

        scene_filename_formats = self.settingsHandler.getValue('scene_filename_formats', [])
        
        # read collection folders and get video paths
        if quick_start:
            print('Loading existing videos from videos handler ...')
            start = time.time()
            existing_videos_dict = self.videosHandler.jsonObject
            self.videos_dict = ff.getLinkedVideosFromJson(existing_videos_dict)
            print('Done. Loaded {} videos in {:.2f}s'.format(len(self.videos_dict), (time.time()-start)))
        else:
            include_folders, ignore_folders, collections_dict = process.readFoldersAndCollections( os.path.join( data_dir, 'video_folders.txt' ) )
            if include_folders == None:
                print("ERROR: No input folders found in:", 'videos.json')
                return
            video_paths = process.getVideosInFolders(include_folders, ignore_folders, include_extensions=VIDEO_EXTENSIONS)
            print("Found {} videos in {} folders from UNKNOWN collections".format(len(video_paths), len(include_folders)))
            # process videos
            print("Processing videos ...")
            start = time.time()
            self.videos_dict = process.processVideos(video_paths, self.videosHandler, collections_dict, scene_filename_formats, reparse_filenames=reparse_filenames, show_collisions=False)
            print("Successfully loaded {} videos (took {:.2f}s)\n".format(len(self.videos_dict), (time.time()-start)))
        
        # self.load_tfidf(regen_tfidf_profiles, recalculate_performer_embeddings)

        if purge_unloaded_video_objects:
            print('Cleaning videos.json file ...')
            self.videosHandler.backup()
            self.videosHandler.jsonObject = self.videos_dict
            self.videosHandler.save()

        if backup_videos_handler:
            self.videosHandler.backup()


    def load_tfidf(self, regen_tfidf_profiles: bool = False, recalculate_performer_embeddings: bool = False):
        """  """
        tfidf_model_fn = 'data/tfidf_model.pkl'
        performer_embeddings_fn = 'data/performer_embeddings.pkl'
        studio_embeddings_fn = 'data/studio_embeddings.pkl'
        tfidf_model = ff.pickle_load(tfidf_model_fn)
        retrain_model = (tfidf_model==None or regen_tfidf_profiles)
        if tfidf_model and not regen_tfidf_profiles:
            print('[TFIFD] Loaded TF-IDF model')
            if ff.newHashNotInTFIDF(self.videos_dict.keys(), tfidf_model['hash_index_map']):
                print('[TFIFD] Found novel video hashes, retraining ...')
                retrain_model = True
        if retrain_model:
            print('[TFIFD] Generating TF-IDF model ...')
            start = time.time()
            tfidf_model = tfidf.generate_tfidf_model(self.videos_dict.values())
            print('[TFIFD] Done. Took {:.2f}s'.format(time.time()-start))
            print('[TFIFD] Saving TF-IDF model ...')
            ff.pickle_save(tfidf_model, tfidf_model_fn)
        performer_embeddings = ff.pickle_load(performer_embeddings_fn)
        if (not performer_embeddings or recalculate_performer_embeddings) and tfidf_model:
            print('[TFIDF] Generating performer profiles ...')
            embeddings, name_index_map, video_count = ff.generate_performer_embeddings(self.videos_dict.values(), tfidf_model['matrix'], tfidf_model['hash_index_map'])
            performer_embeddings = { 'embeddings': embeddings, 'name_index_map': name_index_map, 'video_count': video_count }
            print('[TFIFD] Saving performer embeddings ...')
            ff.pickle_save(performer_embeddings, performer_embeddings_fn)

    def gen_media(self, args):
        """ handle media generation options """
        # videos_to_gen = self.videos_dict.values()
        # bf = ff
        # try:
        #     if args.generate_media or args.generate_teasers:
        #         print(' \nAdding teasers to all media')
        #         bf.mediaAll_generateTeasersSmall(videos_to_gen, MEDIADIR, limit=args.limit, redo=args.redo)
        #     if args.generate_media or args.generate_preview_thumbs:
        #         print('\nAdding seek thumbnails to all media')
        #         n_frames = args.preview_thumbs_nframes if args.preview_thumbs_nframes else 30*10
        #         bf.mediaAll_generatePreviewThumbnails(videos_to_gen, MEDIADIR, redo=args.redo, n_frames=n_frames)
        #     if args.generate_media or args.generate_seek_thumbs:
        #         print('\nAdding seek thumbnails to all media')
        #         bf.mediaAll_generateSeekThumbnails(videos_to_gen, MEDIADIR)
        # except KeyboardInterrupt:
        #     print("[INTERRUPT] Media generation interrupted")

        # if args.link_custom_thumbs:
        #     print('LINKING THUMBS ...')
        #     self.videos_dict = ff.link_custom_thumbs(self.videos_dict, CUSTOM_THUMBS_DIR)

    # endregion
    
    # region MODIFY

    def add_post(self, post):
        with self._lock:  # Locking the method to protect shared state
            ...

    def remove_post(self, post):
        with self._lock:  # Locking the method to protect shared state
            ...

    def update_post(self, post, data):
        with self._lock:  # Locking the method to protect shared state
            ...

    # endregion