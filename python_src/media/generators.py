""" 
A few simple generators (when handymatt-media is not needed)
"""
import os
import subprocess

from handymatt_media.media_generator import generateVideoTeaser

from .checkers import get_video_media_dir



def generatePosterSimple(video_path: str, video_hash: str, mediadir: str, duration_sec: float) -> str|None:
    """ For given video path and hash, generates simple poster into mediadir and returns poster relative path """
    if not os.path.exists(video_path):
        raise FileNotFoundError("Video path doesn't exist:", video_path)
    poster_path = f'{get_video_media_dir(mediadir, video_hash)}/poster.png'
    os.makedirs( os.path.dirname(poster_path), exist_ok=True )
    command = [
        'ffmpeg', 
        '-ss', f'{duration_sec*0.2}',
        '-i', video_path,
        '-frames:v', "1",
        poster_path,
        '-loglevel', 'quiet',
    ]
    subprocess.run(command)
    
    # ensure file exists
    if not os.path.exists(poster_path):
        raise FileExistsError("Poster doesn't exist after creation attempt")
    
    return 'poster.png' # _path_relative_to(poster_path, mediadir)



def generateTeaserSmall(path: str, video_hash: str, mediadir: str, duration_sec: int|float, quiet=True) -> str:
    outfolder = get_video_media_dir(mediadir, video_hash)
    os.makedirs(outfolder, exist_ok=True)
    clip_amount = int( ( 584/119 + (11/5355)*duration_sec ) * 2 )
    if not quiet: print("clip amount:", clip_amount)
    try:
        return generateVideoTeaser(
            path,
            outfolder,
            'teaser_small.mp4',
            abs_amount_mode=True,
            n=clip_amount,
            clip_len=1.3,
            skip=2,
            small_resolution=True,
            end_perc=98,
        )
    except Exception as e:
        print("[ERROR] generateTeasersSmall:\n", e)
        return ""



def generateTeaserLarge(path, hash, mediadir, duration_sec):
    outfolder = get_video_media_dir(mediadir, hash)
    if not os.path.exists(outfolder):
        print("Making folder: ", outfolder)
        os.makedirs(outfolder)
    clip_amount = int( ( 584/119 + (11/5355)*duration_sec ) * 2 )
    try:
        return generateVideoTeaser(
            path,
            outfolder,
            'teaser_large.mp4',
            abs_amount_mode=True,
            n=clip_amount,
            clip_len=1.65,
            skip=1,
            small_resolution=False,
            end_perc=98,
        )
    except Exception as e:
        print("[ERROR] generateTeasersLarge:\n", e)
        return "NULL_PATH"



