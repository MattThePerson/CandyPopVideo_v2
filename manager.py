import argparse

from backend.util.load import scanVideos
from config import COLLECTIONS


def main(args):
    
    if args.scan:
        print('[[MAIN]] Scanning videos ...')
        scanVideos(COLLECTIONS, rehash_videos=args.rehash_videos)
    else:
        print('No arguments passed')









if __name__ == '__main__':
    
    parser = argparse.ArgumentParser('Backend manager for CandyPop Video')
    
    parser.add_argument('-scan', action='store_true', help='Scan videos in collections')
    parser.add_argument('--rehash-videos', '-rv', action='store_true', help='Rehash videos')
    
    args = parser.parse_args()
    
    print()
    try:
        main(args)
    except KeyboardInterrupt:
        print('\n... caught keyboard interrupt')
    print()
    