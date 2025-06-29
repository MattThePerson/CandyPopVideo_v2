from pathlib import Path
import os


def get_video_media_dir(mediadir: str, video_hash: str) -> str:
    """ gets path to videos media directory {mediadir}/videos/0x{videohash}/"""
    return f'{mediadir}/0x{video_hash}'


def path_relative_to(path: str, dirpath: str) -> str:
    return str(Path(path).relative_to(Path(dirpath)))

def confirm_file_parent_exists(path: str):
    if os.path.isfile(path):
        path = os.path.dirname(path)
    os.makedirs(path, exist_ok=True)

