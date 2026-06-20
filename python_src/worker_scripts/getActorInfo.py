"""

"""
import argparse
import json
from python_src.server.api import actor_api


def main(name: str, actor_info_dir: str, redo: bool = False):
    """  """
    api_info = actor_api.get_actor_info(name, actor_info_dir)
    if api_info is None:
        api_info = actor_api.fetch_actor_info(name, actor_info_dir)
    info = {}
    if api_info:
        info = api_info
    return info


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-name', type=str)
    parser.add_argument('-redo', type=bool)
    parser.add_argument('--actor-info-dir', default=None, help='Directory for actor info cache')

    args = parser.parse_args()

    from python_src.util import config
    actor_info_dir = args.actor_info_dir if args.actor_info_dir else config.ACTOR_INFO_DIR

    info = main(args.name, actor_info_dir, args.redo)
    print(json.dumps(info))
