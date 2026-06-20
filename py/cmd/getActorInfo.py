"""
Fetches actor info from cache or scrapes Babepedia, returns JSON to stdout.

Usage:
    python -m cmd.getActorInfo --name "Jane Doe" --actor-info-dir <path>

Output (JSON to stdout):
    {} if not found, otherwise the info dict.
"""
import argparse
import json
import sys

from lib.actor.actor_api import get_actor_info, fetch_actor_info


def main(name: str, actor_info_dir: str) -> dict:
    info = get_actor_info(name, actor_info_dir)
    if info is None:
        info = fetch_actor_info(name, actor_info_dir)
    return info or {}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True, help='Actor name')
    parser.add_argument('--actor-info-dir', required=True, help='Path to actor info cache directory')
    args = parser.parse_args()

    try:
        result = main(args.name, args.actor_info_dir)
        print(json.dumps(result))
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
