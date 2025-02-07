import argparse
import os
from flask import Flask
from multiprocessing import Process, Queue

from backend.app_state import AppState
from backend.flask_routes import server


def media_generator_process(task_queue, result_queue):
    while True:
        task = task_queue.get()
        if task is None:
            break

        video_hash, generator_func = task
        res = generator_func(..., video_hash)
        if res:
            result_queue.put((video_hash, res))
        else:
            result_queue.put(video_hash, False)


def main(args):
    """  """

    PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

    DATA_DIR = os.path.join( PROJECT_DIR, 'data' )

    task_queue = Queue()
    result_queue = Queue()
    worker_process = Process(target=media_generator_process, args=(task_queue, result_queue,), daemon=True)

    state = AppState()
    state.load(
        DATA_DIR,
        quick_start = args.quick_start,
    )

    
    # Flask server start
    if not args.no_start:
        worker_process.start()
        app = Flask(__name__)
        app.register_blueprint(server)
        try:
            app.run(host="0.0.0.0", port=5011)
        except KeyboardInterrupt:
            print('\n... interrupted')
        print('Terminating worker process ...')
        worker_process.terminate()
        worker_process.join()





# INIT
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-nostart', action='store_true', help='')
    parser.add_argument('-qs', '--quick-start', action='store_true', help='Start quickly')
    parser.add_argument('-gm',  '--generate-media', action='store_true', help='Generates all preview and seek media')
    parser.add_argument('-gt',  '--generate-teasers', action='store_true', help='Generates the short clips that tease (or preview) search results')
    parser.add_argument('-gtt',  '--generate-teaser-thumbs', action='store_true', help='Generates thumbnails that show when moving cursor horizontally over video result') # NOT IMPLEMENTED
    parser.add_argument('-gtl', '--generate-teasers-large', action='store_true', help='Generate longer and larger res teasers (NO USE CURRENTLY)') # NOT IMPLEMENTED
    parser.add_argument('-gst', '--generate-seek-thumbs', action='store_true', help='')
    parser.add_argument('-gpt', '--generate-preview-thumbs', action='store_true', help='')

    parser.add_argument('-tfidf_retrain', action='store_true', help='Retrains TF-IDF search model')
    parser.add_argument('-embeddings_regen', action='store_true', help='Retrains performer & studio embeddings')

    parser.add_argument('-link_custom_thumbs', action='store_true', help='Link custom thumbnails to existing videos')
    parser.add_argument('-preview_thumbs_nframes', help='Determine number of frames to skip when extracting temp stills for preview frames generation')

    parser.add_argument('--filter', '-f', help='')
    parser.add_argument('-collections', help='Limit collections loaded. separate collection names with space.')
    parser.add_argument('-load_all', action='store_true', help='Ignore filter for loading of videos')
    parser.add_argument('-show_collisions', action='store_true', help='Print hash collisions')
    parser.add_argument('-limit', help='')
    parser.add_argument('-redo', action='store_true', help='Redo media generation')
    parser.add_argument('--backup', '-b', action='store_true', help='Make a backup of videos.json')
    parser.add_argument('-clean_json', action='store_true', help='Cleans the videos.json')
    parser.add_argument('-reparse', action='store_true', help='Parses all filenames for scene data')

    args = parser.parse_args()
    if args.limit: args.limit = int(args.limit)
    if args.filter: args.filter = args.filter.lower()
    if args.preview_thumbs_nframes: args.preview_thumbs_nframes = int(args.preview_thumbs_nframes)

    if args.clean_json and (args.filter or args.collections):
        print('Cannot use -clean_json with -filter or -collections')
        exit()

    print()
    main(args)
    print()
    
