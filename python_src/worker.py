import argparse

GENERATE_MEDIA_OPTIONS = [ 'all', 'teasers', 'teasers_large', 'teaser_thumbs', 'teaser_thumbs_large', 'preview_thumbs', 'seek_thumbs' ]


def backend_manager(args: argparse.Namespace, ws=None):
    import yaml
    import random
    from datetime import datetime
    
    from python_src.util import db
    from python_src.util.config import PREVIEW_MEDIA_DIR, TFIDF_MODEL_PATH
    from python_src.util.general import pickle_save
    from python_src.schemas import VideoData, SearchQuery, TFIDFModel

    from python_src.recommender.search import filterVideoObjects
    from python_src.recommender.tfidf import generate_tfidf_model
    from python_src.scan import scan
    from python_src.media import mass_generators
    
    """
    Backend manager for CandyPop Video. Can be used from CL or via websocket
        
    Used for:
    - scanning/rescanning libraries
    - generating preview media
    - showing status of media library
    """
    
    # 
    if args.update:
        print('Using --update. Scanning libraries & generating media')
        args.path_include_filters = args.update
        args.scan_libraries = True
        args.reparse_filenames = True
        args.reread_json_metadata = True
        args.generate_media = 'all'
        args.media_status = 'all'
    
    if args.update_media: # hours
        print('Updating all media added in last {} hours'.format(args.update_media))
        ts = datetime.now().timestamp() - args.update_media * 3600 # timestamp (float) in seconds
        args.date_added_from = str( datetime.fromtimestamp(ts) )[:-10]
        args.generate_media = 'all'
        args.media_status = 'all'
    
    if args.redo_info:
        args.reparse_filenames = True
        args.reread_json_metadata = True
    
    # HELPERS
    
    def get_linked_videos():
        video_dicts = db.read_table_as_dict('videos')
        return [ VideoData.from_dict(dct) for hsh, dct in video_dicts.items() if dct.get('is_linked') ]


    def filter_videos_with_args(videos_list: list[VideoData], args: argparse.Namespace) -> list[VideoData]:
        query = SearchQuery(
            search_string = "NULL_STRING",
            actor = args.actor,
            studio = args.studio,
            collection = args.select_collection,
            include_terms = [ x.strip() for x in args.path_include_filters.split(',') ]     if args.path_include_filters         else [],
            exclude_terms = [ x.strip() for x in args.path_exclude_filters.split(',') ]     if args.path_exclude_filters else [],
            date_added_from = args.date_added_from,
            date_added_to = args.date_added_to,
            date_released_from = None,
            date_released_to = None,
            only_favourites = False,
            sortby = "date_added",
            limit = -1,
            startfrom = 0,
        )
        filtered = filterVideoObjects(videos_list, query)
        if args.last_videos_added:
            return filtered[:args.last_videos_added]
        return filtered
    

    # HANDLE
    
    if args.scan_libraries: # - SCAN ---------------------------------------------------------------
        print('[MAIN] Scanning videos ...')
        with open('config.yaml', 'r') as f:
            CONFIG = yaml.safe_load(f)
        COLLECTIONS = CONFIG.get('collections')
        scan.scanVideos(
            COLLECTIONS,
            rehash_videos=args.rehash_videos,
            redo_video_attributes=args.redo_video_attributes,
            reparse_filenames=args.reparse_filenames,
            reread_json_metadata=args.reread_json_metadata,
            path_filters=args.path_include_filters,
            ws=ws
        )
        # generate tfidf model
        print('Generating tfidf model for videos')
        videos_list = get_linked_videos()
        model: TFIDFModel = generate_tfidf_model(videos_list)
        print('Saving model to:', TFIDF_MODEL_PATH)
        pickle_save(model, TFIDF_MODEL_PATH)
    

    if args.generate_media: # - MEDIA --------------------------------------------------------------
        # filter videos
        print('[GET] getting and filtering linked videos')
        videos_list = get_linked_videos()
        filtered_videos = filter_videos_with_args(videos_list, args)

        if args.randomize:
            random.shuffle(filtered_videos)
        else:
            filtered_videos.sort(reverse=True, key=lambda vd: vd.date_added)
        
        # call generators
        print('[START] Generating media for {} videos'.format(len(filtered_videos)))
        alist = [ filtered_videos, PREVIEW_MEDIA_DIR ]
        kdict = { "redo": args.redo_media_gen, "limit": args.limit, "ws": ws }
        opt = args.generate_media
        succs, fails = {}, {}
        if opt == 'all' or opt == 'teaser_thumbs': 
            succ, fail = mass_generators.mass_generate_teaser_thumbs_small( *alist, **kdict )
            succs['teaser_thumbs'] = succ
            fails['teaser_thumbs'] = fail
        if opt == 'all' or opt == 'teasers':       
            succ, fail = mass_generators.mass_generate_teasers_small( *alist, **kdict )
            succs['teasers'] = succ
            fails['teasers'] = fail
        if opt == 'all' or opt == 'seek_thumbs':   
            succ, fail = mass_generators.mass_generate_seek_thumbs( *alist, **kdict )
            succs['seek_thumbs'] = succ
            fails['seek_thumbs'] = fail
        if opt == 'all' or opt == 'preview_thumbs':
            succ, fail = mass_generators.mass_generate_preview_thumbs( *alist, **kdict )
            succs['preview_thumbs'] = succ
            fails['preview_thumbs'] = fail
        # if opt == 'all' or opt == 'teasers_large': 
        #     succ, fail = generate.mass_generate_teasers_large( *alist, **kdict )
        #     succs['teasers_large'] = succ
        #     fails['teasers_large'] = fail
        # if opt == 'all' or opt == 'teaser_thumbs_large': 
        #     succ, fail = generate.mass_generate_teaser_thumbs_large( *alist, **kdict )
        #     succs['teaser_thumbs_large'] = succ
        #     fails['teaser_thumbs_large'] = fail
        # try:
        # except KeyboardInterrupt:
        #     print('\n... interrupting')
        
        print('\n  WORK REPORT:\n')
        print('TYPE                   GENERATION COUNT')
        succs['total'] = []
        fails['total'] = []
        for k, s in succs.items():
            f = fails[k]
            fails_str = ' ({:_} fails)'.format(len(f)) if f != [] else ''
            print('{:<25} : {:_}{}'.format(k, len(s), fails_str))
            if k != 'total':
                succs['total'].extend(s)
                fails['total'].extend(f)
        print()
        

    if args.generate_tfidf:
        print('Generating tfidf model for videos')
        videos_list = get_linked_videos()
        model: TFIDFModel = generate_tfidf_model(videos_list)
        print('Saving model to:', TFIDF_MODEL_PATH)
        pickle_save(model, TFIDF_MODEL_PATH)


    if args.generate_embeddings:
        print('Generating performer and studio embeddings from videos TF-IDF model')
        ...
        

    if args.media_status: # - MEDIA STATUS ---------------------------------------------------------
        print("filtering videos ...")
        videos_list = get_linked_videos()
        filtered_videos = filter_videos_with_args(videos_list, args)
        print("Video Filters:")
        print('{:<20} : {}'.format("performer", args.actor))
        print('{:<20} : {}'.format("studio", args.studio))
        print('{:<20} : {}'.format("filters", args.path_include_filters))
        print('{:<20} : {}'.format("select_collection", args.select_collection))
        print(f"\nPREVIEW MEDIA STATUS FOR {len(filtered_videos)} VIDEOS:")
        mass_generators.checkPreviewMediaStatus(filtered_videos, PREVIEW_MEDIA_DIR, args.media_status, print_without=args.print_without)
        

    elif args.status: # - STATUS -------------------------------------------------------------------
        print("STATUS OF LOADED VIDEOS:")
        videos_list = get_linked_videos()
        filtered_videos = filter_videos_with_args(videos_list, args)
        colls = {}
        for vd in filtered_videos:
            colls[vd.collection] = colls.get(vd.collection, 0) + 1
        print("collection    | videos")
        collections = sorted(colls.keys(), reverse=True, key=lambda k: colls[k])
        for c in collections:
            print('{:>13} : {:_}'.format(c, colls[c]))
        print('{:>13} : {:_}'.format('total', len(filtered_videos)))
        


#region - ARGUMENT PARSER ----------------------------------------------------------------------------------------------

# Inheriting class that doesnt call sys.exit()
class NoExitArgumentParser(argparse.ArgumentParser):
    """ Non exiting argument parser, for use in a REPL """
    
    def exit(self, status=0, message=None):
        if message:
            raise argparse.ArgumentError(None, message)
        raise argparse.ArgumentError(None, f"Exited with status {status}")

    def error(self, message):
        raise argparse.ArgumentError(None, message)


# get argument parser instance
def create_argument_parser(non_exiting=False):

    if non_exiting:
        parser = NoExitArgumentParser()
    else:
        parser = argparse.ArgumentParser()


    
    # [1] Status
    parser.add_argument('--media-status', '-ms',                                help='[check] Get generation status of preview media', choices=GENERATE_MEDIA_OPTIONS, type=str)
    parser.add_argument('--status', action='store_true',                        help='[check] Get amount of videos and collections')
    parser.add_argument('--print-without', nargs='?', const=10, default=0,      help='[check] Print paths of videos without', type=int)
    # parser.add_argument('--media',                  action='store_true',        help='')
    parser.add_argument('--cull-unlinked-media',    action='store_true',        help='')

    # [2] Library scanning
    parser.add_argument('--scan-libraries', '-sl',  action='store_true',        help='')
    parser.add_argument('--rehash-videos',          action='store_true',        help='[scan]')
    parser.add_argument('--reparse-filenames',          action='store_true',    help='[scan]')
    parser.add_argument('--reread-json-metadata',   action='store_true',        help='[scan]')
    parser.add_argument('--redo-video-attributes',   action='store_true',       help='[scan]')
    parser.add_argument('--generate-tfidf',            action='store_true',     help='')
    parser.add_argument('--generate-embeddings',       action='store_true',     help='')

    # [3] Media generation
    parser.add_argument('--generate-media', '-gm',                              help='opts=[all|teasers|teasers_large|teaser_thumbs|teaser_thumbs_large|preview_thumbs|seek_thumbs]', choices=GENERATE_MEDIA_OPTIONS)
    parser.add_argument('--redo-media-gen',        action='store_true',         help='[media_gen] redo media gen (replace old)')
    
    parser.add_argument('--actor',                                              help='[media_gen] ')
    parser.add_argument('--studio',                                             help='[media_gen] ')
    
    parser.add_argument('--path-include-filters', '-f',                         help='[scan|media_gen] for which videos to generate media for | separated by comma')
    parser.add_argument('--path-exclude-filters', '-xf',                        help='[scan|media_gen] for which videos to generate media for | separated by comma')
    parser.add_argument('--limit', '-l', type=int,                              help='[media_gen]')
    parser.add_argument('--sortby',                                             help='[media_gen]')
    parser.add_argument('--date-added-from', '-since',                          help='[media_gen]')
    parser.add_argument('--date-added-to', '-till',                             help='[media_gen]')
    parser.add_argument('--last-videos-added', '-last', type=int,               help='[media_gen] Select last x videos that were added')
    parser.add_argument('--select-collection', '-sc',                           help='Select collection to')
    parser.add_argument('--randomize', action='store_true',                     help='Randomize selected videos to avoid generating media for faulty videos first')

    parser.add_argument('--update', '-u',                                       help='[Path filter] for which to scan libraries & generate media all')
    parser.add_argument('--update-media', '-um', type=float,                    help='[Number of hours] for which to Generate all preview media')
    parser.add_argument('--redo-info', '-ri',       action='store_true',        help='[scan] combines --reparse-filenames and --reread-json-metadata')

    # 
    # parser.add_argument('--verbose',               action='store_true',         help='')

    return parser



# START FROM CL
if __name__ == '__main__':
    # import asyncio
    # async def backend_manager_cl_entry():
    #     parser = create_argument_parser()
    #     args = parser.parse_args()
    #     print()
    #     backend_manager(args)
    #     print()
    # asyncio.run(backend_manager_cl_entry())

    parser = create_argument_parser()
    args = parser.parse_args()
    backend_manager(args)