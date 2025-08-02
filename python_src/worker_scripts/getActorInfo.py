"""

"""
import argparse
import json
from python_src.server.api import actor_api
from handymatt_media.media_generator import generateVideoTeaser


def main(name: str, redo: bool=False):
    """  """
    api_info = actor_api.get_actor_info(name)
    if api_info is None:
        api_info = actor_api.fetch_actor_info(name)
    info = {}
    if api_info:
        info = api_info
    return info





if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-name', type=str)
    parser.add_argument('-redo', type=bool)
    
    args = parser.parse_args()
    
    info = main(args.name, args.redo)
    print(json.dumps(info))
    