import argparse
from fastapi import WebSocket

from backend.util.load import scanVideos
from config import COLLECTIONS


async def backend_manager(args: argparse.Namespace, ws: WebSocket|None=None):
    """
    Backend manager for CandyPop Video. Can be used from CL or via websocket
        
    Used for:
    - scanning/rescanning libraries
    - generating preview media
    - showing status of media library
    """
    
    # await aprint(ws, 'Welcome to backend manager')
    
    if args.scan_libraries:
        await aprint(ws, 'Scanning videos ...')
        # scanVideos(COLLECTIONS, rehash_videos=args.rehash_videos)
    elif args.limit:
        await aprint(ws, 'limiting to:', args.limit)
    else:
        await aprint(ws, 'No arguments passed')


async def aprint(ws, *args, sep=' ', end='\n'):
    text = sep.join(str(arg) for arg in args) + end
    if ws is None:
        print(text, end='')  # prevent double newline
    else:
        await ws.send_text(text)


class NoExitArgumentParser(argparse.ArgumentParser):
    """ Non exiting argument parser, for use in a REPL """
    
    def exit(self, status=0, message=None):
        if message:
            raise argparse.ArgumentError(None, message)
        raise argparse.ArgumentError(None, f"Exited with status {status}")

    def error(self, message):
        raise argparse.ArgumentError(None, message)


def create_argument_parser(non_exiting=False):

    if non_exiting:
        parser = NoExitArgumentParser()
    else:
        parser = argparse.ArgumentParser()

    # [1] Status
    parser.add_argument('--status',                 action='store_true',        help='')
    parser.add_argument('--media',                  action='store_true',        help='')
    parser.add_argument('--cull-unlinked-media',    action='store_true',        help='')

    # [2] Library scanning
    parser.add_argument('--scan-libraries',         action='store_true',        help='')
    parser.add_argument('--rehash-videos',          action='store_true',        help='')
    parser.add_argument('--reread-json-metadata',   action='store_true',        help='')
    parser.add_argument('--paths-filters',                                      help='')
    parser.add_argument('--paths-exclude-filters',                              help='')
    
    parser.add_argument('--regen-tfidf',            action='store_true',        help='')
    parser.add_argument('--regen-embeddings',       action='store_true',        help='')

    # [3] Media generation
    parser.add_argument('--generate-media',        action='store_true',         help='')
    parser.add_argument('--redo-media-gen',        action='store_true',         help='')
    parser.add_argument('--filters',                                            help='')
    parser.add_argument('--exclude-filters',                                    help='')
    parser.add_argument('--from-collections',                                   help='')
    parser.add_argument('--limit',                 type=int,                    help='')
    parser.add_argument('--sortby',                                             help='')
    parser.add_argument('--date-added-from',                                    help='')
    parser.add_argument('--date-added-to',                                      help='')

    # 
    parser.add_argument('--verbose',               action='store_true',         help='')
    
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
