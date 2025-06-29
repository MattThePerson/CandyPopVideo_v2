import os
from datetime import datetime

from .helpers import get_video_media_dir

def hasPoster(video_hash: str, mediadir: str) -> str|None:
    """ For given hash, returns poster relative path if exists """
    poster_path = os.path.join( get_video_media_dir(mediadir, video_hash), 'poster.png' )
    if not os.path.exists(poster_path):
        return None
    return 'poster.png' #_path_relative_to(poster_path, mediadir)


def hasSeekThumbs(video_hash: str, mediadir: str):
    """ checks if seekthumbs.jpg and seekthumbs.vtt exist in video preview media dir """
    videomediadir = get_video_media_dir(video_hash, mediadir)
    return os.path.exists( videomediadir + '/seekthumbs.jpg') and os.path.exists( videomediadir + '/seekthumbs.vtt' )


def hasTeaserSmall(video_hash: str, mediadir: str) -> bool:
    if hash == -1:
        input("\n\nMINUS ONE")
    teaser_small_path = os.path.join( get_video_media_dir(mediadir, video_hash), 'teaser_small.mp4' )
    return os.path.exists(teaser_small_path)


def hasTeaserLarge(hash, mediadir):
    teaser_large_path = os.path.join( get_video_media_dir(mediadir, hash), 'teaser_large.mp4' )
    return os.path.exists(teaser_large_path)


def hasPreviewThumbs(hash, mediadir, small=True):
    vid_folder = f'{get_video_media_dir(mediadir, hash)}/previewthumbs'
    if not os.path.exists(vid_folder):
        return None
    res = '360' if small else '1080'
    thumb_paths = [ os.path.join('previewthumbs', f) for f in os.listdir(vid_folder) if res in f ] # http://localhost:8000/media/videos/0x0064e4c01f13/poster.png
    if thumb_paths == []:
        return None
    # return thumbnail by second
    delta = (datetime.now() - datetime.strptime('1900', '%Y'))
    i = int(delta.seconds%len(thumb_paths))
    return thumb_paths[i]


def hasCustomThumb(hash, dir):
    fn = f'[{hash}].png'
    if os.path.exists(os.path.join(dir, fn)):
        return fn
    return False



