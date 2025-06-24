import argparse

from backend.util.load import scanVideos
from config import COLLECTIONS


def main(args):
    
    if args.scan:
        print('[[MAIN]] Scanning videos ...')
        scanVideos(COLLECTIONS)










if __name__ == '__main__':
    
    parser = argparse.ArgumentParser('Backend manager for CandyPop Video')
    
    parser.add_argument('-scan', action='store_true', help='Scan videos in collections')
    
    args = parser.parse_args()
    
    print()
    main(args)
    print()
    