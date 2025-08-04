import os
from datetime import datetime


def hasPoster(video_hash: str, mediadir: str) -> str|None:
    """ For given hash, returns poster relative path if exists """
    poster_path = os.path.join( get_video_media_dir(mediadir, video_hash), 'poster.png' )
    if not os.path.exists(poster_path):
        return None
    return 'poster.png' #_path_relative_to(poster_path, mediadir)


def hasSeekThumbs(video_hash: str, mediadir: str):
    """ checks if seekthumbs.jpg and seekthumbs.vtt exist in video preview media dir """
    videomediadir = get_video_media_dir(mediadir, video_hash)
    return os.path.exists( videomediadir + '/seekthumbs.jpg') and os.path.exists( videomediadir + '/seekthumbs.vtt' )


def hasTeaserSmall(video_hash: str, mediadir: str) -> bool:
    if hash == -1:
        input("\n\nMINUS ONE")
    teaser_small_path = os.path.join( get_video_media_dir(mediadir, video_hash), 'teaser_small.mp4' )
    return os.path.exists(teaser_small_path)

def hasTeaserLarge(video_hash: str, mediadir: str):
    teaser_large_path = os.path.join( get_video_media_dir(mediadir, video_hash), 'teaser_large.mp4' )
    return os.path.exists(teaser_large_path)


def hasTeaserThumbsSmall(video_hash: str, mediadir: str):
    videomediadir = get_video_media_dir(mediadir, video_hash)
    return os.path.exists( videomediadir + '/teaser_thumbs_small.jpg' )

def hasTeaserThumbsLarge(video_hash: str, mediadir: str):
    videomediadir = get_video_media_dir(mediadir, video_hash)
    return os.path.exists( videomediadir + '/teaser_thumbs_large.jpg' )


def hasPreviewThumbs(video_hash: str, mediadir: str, large=True):
    vid_folder = f'{get_video_media_dir(mediadir, video_hash)}/previewthumbs'
    if not os.path.exists(vid_folder):
        return None
    dir_contents = os.listdir(vid_folder)
    if len(dir_contents) < 10:
        return None
    res = '1080' if large else '360'
    thumb_paths = [ os.path.join('previewthumbs', f) for f in dir_contents if res in f ]
    if thumb_paths == []:
        return None
    # return thumbnail by second
    delta = (datetime.now() - datetime.strptime('1900', '%Y'))
    i = int(delta.seconds%len(thumb_paths))
    return thumb_paths[i]


def hasCustomThumb(video_hash: str, dir: str):
    fn = f'[{video_hash}].png'
    if os.path.exists(os.path.join(dir, fn)):
        return fn
    return False



def get_video_media_dir(mediadir: str, video_hash: str) -> str:
    """ gets path to videos media directory {mediadir}/videos/0x{videohash}/"""
    return f'{mediadir}/0x{video_hash}'

