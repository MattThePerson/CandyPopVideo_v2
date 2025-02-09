""" 
Functions for handling confirming and generation of preview media
Contents of videos mediadir:
    seekthumbs/
    stills/
    poster.png
    poster_small.png
    teaser_small.mp4
    teaser_large.mp4
"""
import os
import subprocess
import shlex
from datetime import datetime

from handymatt_media import media_generator


def hasPoster(video_hash: str, mediadir: str):
    poster_fn = 'poster.png'
    # poster_path = f'{mediadir}/{hash}/{poster_fn}'
    poster_path = os.path.join( get_video_media_dir(mediadir, video_hash), poster_fn )
    if os.path.exists(poster_path):
        return poster_fn
    return None


def generatePosterSimple(path: str, video_hash: str, mediadir: str, duration_sec: float):
    if not os.path.exists(path):
        return False
    vidmediadir = get_video_media_dir(mediadir, video_hash)
    if not os.path.exists( vidmediadir ):
        os.makedirs(vidmediadir)
    poster_fn = 'poster.png'
    poster_path = os.path.join(vidmediadir, poster_fn)
    command = f'ffmpeg -ss {duration_sec*0.1} -i "{path}" -frames:v 1 "{poster_path}" -loglevel quiet'
    subprocess.run(shlex.split(command))
    if os.path.exists( poster_path ):
        return poster_fn
    return None


def hasSeekThumbs(video_hash: str, mediadir: str, duration_sec: float):
    dir = os.path.join(get_video_media_dir(mediadir, video_hash), 'seekthumbs')
    if not os.path.exists(dir):
        return False
    interval_sec = max( int((5/1920) * duration_sec), 1)
    return len(os.listdir(dir)) >= int(duration_sec / interval_sec)



def generateSeekThumbs(videopath: str, video_hash: str, mediadir: str, duration_sec: float, height=180):
    if not os.path.exists(videopath):
        print("Video doesn't exits:", videopath)
        return False
    seekthumbsdir = os.path.join(get_video_media_dir(mediadir, video_hash), 'seekthumbs')
    if not os.path.exists(seekthumbsdir):
        print("Making dir:", seekthumbsdir)
        os.makedirs(seekthumbsdir)
    thumbpath = os.path.join( seekthumbsdir, 'seekthumb%04d.jpg' )
    interval_sec = max( int((5/1920) * duration_sec), 1)
    print("  SEEK THUMBNAIL INTERVAL:", interval_sec)
    tile = (1, 1)
    command = (
        f'ffmpeg -ss 0 -i "{videopath}" -vsync vfr -v quiet -stats '
        f'-vf "fps=1/{interval_sec},scale=-1:{height},tile={tile[0]}x{tile[1]}" '
        f'-qscale:v 1 "{thumbpath}"'
    )
    subprocess.run(shlex.split(command))
    print("Done.")


# 
def hasTeaserSmall(video_hash: str, mediadir: str) -> bool:
    if hash == -1:
        input("\n\nMINUS ONE")
    teaser_small_path = os.path.join( get_video_media_dir(mediadir, video_hash), 'teaser_small.mp4' )
    return os.path.exists(teaser_small_path)

# 
def generateTeaserSmall(path, hash, mediadir, duration_sec, quiet=True):
    outfolder = get_video_media_dir(mediadir, hash)
    if not os.path.exists(outfolder):
        print("Making folder: ", outfolder)
        os.makedirs(outfolder)
    clip_amount = int( ( 584/119 + (11/5355)*duration_sec ) * 2 )
    if not quiet: print("clip amount:", clip_amount)
    try:
        return media_generator.generateVideoTeaser(path, outfolder, 'teaser_small.mp4', abs_amount_mode=True, n=clip_amount, clip_len=1.3, skip=2, smallSize=True, end_perc=98)
    except Exception as e:
        print("[ERROR] generateTeasersSmall")
        print(e)
        return None

# 
def hasTeaserLarge(hash, mediadir):
    teaser_large_path = os.path.join( get_video_media_dir(mediadir, hash), 'teaser_large.mp4' )
    return os.path.exists(teaser_large_path)

# 
def generateTeaserLarge(path, hash, mediadir, duration_sec):
    outfolder = get_video_media_dir(mediadir, hash)
    if not os.path.exists(outfolder):
        print("Making folder: ", outfolder)
        os.makedirs(outfolder)
    clip_amount = int( ( 584/119 + (11/5355)*duration_sec ) * 2 )
    return media_generator.generateVideoTeaser(path, outfolder, 'teaser_large.mp4', abs_amount_mode=True, n=clip_amount, clip_len=1.65, skip=1, smallSize=False, end_perc=98)

# 
def hasPreviewThumbs(hash, mediadir, small=True):
    vid_folder = os.path.join( get_video_media_dir(mediadir, hash), 'previewthumbs' )
    if not os.path.exists(vid_folder):
        return None
    res = '360' if small else '1080'
    thumb_paths = [ os.path.join('previewthumbs', f) for f in os.listdir(vid_folder) if res in f ]
    if thumb_paths == []:
        return None
    delta = (datetime.now() - datetime.strptime('1900', '%Y'))
    # i = int(delta.days%len(thumbs_small))
    i = int(delta.seconds%len(thumb_paths))
    return thumb_paths[i]

# 
def hasCustomThumb(hash, dir):
    fn = f'[{hash}].png'
    if os.path.exists(os.path.join(dir, fn)):
        return fn
    return False

# 
def generatePreviewThumbs(path, hash, mediadir, amount=5, n_frames=30*10):
    vid_folder = os.path.join( get_video_media_dir(mediadir, hash), 'previewthumbs' )
    os.makedirs(vid_folder, exist_ok=True)
    paths = media_generator.extractPreviewThumbs(path, vid_folder, amount=amount, resolution=[360, 1080], n_frames=n_frames)


#### MASS GENERATE ####

# 
def generateTeasersSmallForVideos(videos, mediadir, limit=None, redo=False):
    succ, fails = [], []
    for i, vid in enumerate(videos):
        hash = vid['hash']
        print("\r  ({}/{}) generating small teasers ({} fails) [{}] {:<120}     ".format( i+1, len(videos), len(fails), hash, f"{vid['path'][:118]}" ), end='')
        if hash != -1 and (redo or not hasTeaserSmall(hash, mediadir)):
            teaser_path = generateTeaserSmall(vid['path'], hash, mediadir, vid['duration_seconds'])
            if teaser_path == None or not os.path.exists(teaser_path):
                fails.append(vid)
            else:
                succ.append(vid)
                if limit and len(succ) >= limit:
                    break

# 
def generateSeekThumbnailsForVideos(videos, mediadir):
    succ, fails = [], []
    for i, vd in enumerate(videos):
        hash = vd['hash']
        if not hasSeekThumbs(hash, mediadir, vd['duration_seconds']):
            print("\r  ({}/{}) generating seek thumbs  {:<80}    ".format(i+1, len(videos), f"{vd['path'][:76]}"), end='')
            generateSeekThumbs(vd['path'], hash, mediadir, vd['duration_seconds'])

#
def generatePreviewThumbnailsForVideos(videos, mediadir, redo=False, n_frames=30*10):
    succ, fails = [], []
    for i, vd in enumerate(videos):
        hash = vd['hash']
        if redo or not hasPreviewThumbs(hash, mediadir, small=True):
            print("\r  ({}/{}) generating preview thumbnails [{}]  {:<80}    ".format(i+1, len(videos), hash, f"{vd['path'][:76]}"), end='')
            generatePreviewThumbs(vd['path'], hash, mediadir, amount=5, n_frames=n_frames)


#### HELPERS ####


def get_video_media_dir(mediadir: str, video_hash: str) -> str:
    return os.path.join( mediadir, '0x' + video_hash )