import argparse
# from fastapi import WebSocket

GENERATE_MEDIA_OPTIONS = [ 'all', 'teasers', 'teasers_large', 'teaser_thumbs', 'teaser_thumbs_large', 'preview_thumbs', 'seek_thumbs' ]


async def backend_manager(args: argparse.Namespace, ws=None):
    import yaml

    from app import db
    from app.schemas import VideoData, SearchQuery, TFIDFModel
    from config import PREVIEW_MEDIA_DIR
    from app.backend import generate, scan
    from app.backend.helpers import aprint
    from app.recommender.search import filterVideoObjects
    from app.recommender.tfidf import generate_tfidf_model
    """
    Backend manager for CandyPop Video. Can be used from CL or via websocket
        
    Used for:
    - scanning/rescanning libraries
    - generating preview media
    - showing status of media library
    """
    
    if args.scan_libraries: # - SCAN ---------------------------------------------------------------
        await aprint(ws, '[MAIN] Scanning videos ...')
        with open('config.yaml', 'r') as f:
            CONFIG = yaml.safe_load(f)
        COLLECTIONS = CONFIG.get('collections')
        await scan.scanVideos(COLLECTIONS, rehash_videos=args.rehash_videos, ws=ws)
    
    # load video objects
    video_dicts = db.read_table_as_dict('videos')
    videos_list = [ VideoData.from_dict(dct) for hsh, dct in video_dicts.items() if dct.get('is_linked') ]
    
    if args.generate_media: # - MEDIA ------------------------------------------------------------
        # filter videos
        query = SearchQuery(
            search_string = "NULL_STRING",
            performer = args.performer,
            studio = args.studio,
            collection = args.select_collection,
            include_terms = [ x.strip() for x in args.filters.split(',') ]          if args.filters         else [],
            exclude_terms = [ x.strip() for x in args.exclude_filters.split(',') ]  if args.exclude_filters else [],
            date_added_from = args.date_added_from,
            date_added_to = args.date_added_to,
            date_released_from = None,
            date_released_to = None,
            only_favourites = False,
            sortby = "date_added",
            limit = -1,
            startfrom = 0,
        )
        filtered_videos = filterVideoObjects(videos_list, query)
        
        # call generators
        await aprint(ws, 'Generating media for {} videos'.format(len(filtered_videos)))
        alist = [ filtered_videos, PREVIEW_MEDIA_DIR ]
        kdict = { "redo": args.redo_media_gen, "limit": args.limit, "ws": ws }
        opt = args.generate_media
        succs, fails = {}, {}
        try:
            if opt == 'all' or opt == 'teasers':       
                succ, fail = await generate.mass_generate_teasers_small( *alist, **kdict )
                succs['teasers'] = succ
                fails['teasers'] = fail
            if opt == 'all' or opt == 'preview_thumbs':
                succ, fail = await generate.mass_generate_preview_thumbs( *alist, **kdict )
                succs['preview_thumbs'] = succ
                fails['preview_thumbs'] = fail
            if opt == 'all' or opt == 'seek_thumbs':   
                succ, fail = await generate.mass_generate_seek_thumbs( *alist, **kdict )
                succs['seek_thumbs'] = succ
                fails['seek_thumbs'] = fail
            # if opt == 'all' or opt == 'teasers_large': 
            #     succ, fail = await generate.mass_generate_large_teasers( *alist, **kdict )
            #     succs['teasers_large'] = succ
            #     fails['teasers_large'] = fail
            if opt == 'all' or opt == 'teaser_thumbs': 
                succ, fail = await generate.mass_generate_teaser_thumbs_small( *alist, **kdict )
                succs['teaser_thumbs'] = succ
                fails['teaser_thumbs'] = fail
            if opt == 'all' or opt == 'teaser_thumbs_large': 
                succ, fail = await generate.mass_generate_teaser_thumbs_large( *alist, **kdict )
                succs['teaser_thumbs_large'] = succ
                fails['teaser_thumbs_large'] = fail
        except KeyboardInterrupt:
            await aprint(ws, '\n... interrupting')
        
        await aprint(ws, '\n  WORK REPORT:\n')
        await aprint(ws, 'TYPE                   GENERATION COUNT')
        succs['total'] = []
        fails['total'] = []
        for k, s in succs.items():
            f = fails[k]
            fails_str = ' ({:_} fails)'.format(len(f)) if f != [] else ''
            await aprint(ws, '{:<25} : {:_}{}'.format(k, len(s), fails_str))
            if k != 'total':
                succs['total'].extend(s)
                fails['total'].extend(f)
        await aprint(ws, )
        

    if args.generate_tfidf:
        await aprint(ws, 'Generating tfidf model for videos')
        from config import TFIDF_MODEL_PATH
        from app.util.general import pickle_save
        model: TFIDFModel = generate_tfidf_model(videos_list)
        await aprint(ws, 'Saving model to:', TFIDF_MODEL_PATH)
        pickle_save(model, TFIDF_MODEL_PATH)


    if args.generate_embeddings:
        await aprint(ws, 'Generating performer and studio embeddings from videos TF-IDF model')
        ...
        

    if args.status: # - STATUS -------------------------------------------------------------------
        await aprint(ws, "Status:")
        ...

    # if not args.status and not args.generate_media and not args.scan_libraries:
    #     await aprint(ws, 'No arguments passed')




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
    parser.add_argument('--status',                 action='store_true',        help='')
    # parser.add_argument('--media',                  action='store_true',        help='')
    parser.add_argument('--cull-unlinked-media',    action='store_true',        help='')

    # [2] Library scanning
    parser.add_argument('--scan-libraries', '-sl',  action='store_true',        help='')
    parser.add_argument('--rehash-videos',          action='store_true',        help='[scan]')
    parser.add_argument('--reread-json-metadata',   action='store_true',        help='[scan]')
    parser.add_argument('--generate-tfidf',            action='store_true',        help='')
    parser.add_argument('--generate-embeddings',       action='store_true',        help='')

    parser.add_argument('--paths-filters',                                      help='[scan]') # if called, non scanning wont flip is_linked flag
    parser.add_argument('--paths-exclude-filters',                              help='[scan]') # if called, non scanning wont flip is_linked flag
    

    # [3] Media generation
    parser.add_argument('--generate-media', '-gm',                              help='opts=[all|teasers|teasers_large|teaser_thumbs|teaser_thumbs_large|preview_thumbs|seek_thumbs]', choices=GENERATE_MEDIA_OPTIONS)
    parser.add_argument('--redo-media-gen',        action='store_true',         help='[media_gen] redo media gen (replace old)')
    
    parser.add_argument('--performer',                                          help='[media_gen] ')
    parser.add_argument('--studio',                                             help='[media_gen] ')
    
    parser.add_argument('--filters', '-f',                                      help='[media_gen] for which videos to generate media for | separated by comma')
    parser.add_argument('--exclude-filters',                                    help='[media_gen] for which videos to generate media for | separated by comma')
    parser.add_argument('--limit',                 type=int,                    help='[media_gen]')
    parser.add_argument('--sortby',                                             help='[media_gen]')
    parser.add_argument('--date-added-from',                                    help='[media_gen]')
    parser.add_argument('--date-added-to',                                      help='[media_gen]')
    parser.add_argument('--select-collection', '-sc',                           help='Select collection to')
    

    # 
    # parser.add_argument('--verbose',               action='store_true',         help='')

    return parser



# START FROM CL
if __name__ == '__main__':
    import asyncio
    
    async def backend_manager_cl_entry():
        parser = create_argument_parser()
        args = parser.parse_args()
        print()
        await backend_manager(args)
        print()
    
    asyncio.run(backend_manager_cl_entry())
