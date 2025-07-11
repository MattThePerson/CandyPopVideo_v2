# TODO: Determine if needs to be removed / refactored
""" 
Functions for handling confirming and generation of preview media
Contents of videos mediadir:
    seekthumbs/
    stills/
    teaser_thumbs/
    poster.png
    poster_small.png
    teaser_small.mp4
    teaser_large.mp4
"""
import os
from pathlib import Path
import subprocess
import shlex

from handymatt_media import media_generator

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



# TODO: DEPRECATED! Remove
def generateSeekThumbs_ffmpeg(videopath: str, video_hash: str, mediadir: str, duration_sec: float, height=180):
    """ Uses ffmpeg to generate seek thumbnails (HUOM: Doesn't generate spritesheet) """
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


def generateTeaserSmall(path: str, video_hash: str, mediadir: str, duration_sec: int|float, quiet=True) -> str:
    outfolder = get_video_media_dir(mediadir, video_hash)
    if not os.path.exists(outfolder):
        print("Making folder: ", outfolder)
        os.makedirs(outfolder)
    clip_amount = int( ( 584/119 + (11/5355)*duration_sec ) * 2 )
    if not quiet: print("clip amount:", clip_amount)
    try:
        return media_generator.generateVideoTeaser(path, outfolder, 'teaser_small.mp4', abs_amount_mode=True, n=clip_amount, clip_len=1.3, skip=2, smallSize=True, end_perc=98)
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
        return media_generator.generateVideoTeaser(path, outfolder, 'teaser_large.mp4', abs_amount_mode=True, n=clip_amount, clip_len=1.65, skip=1, smallSize=False, end_perc=98)
    except Exception as e:
        print("[ERROR] generateTeasersSmall:\n", e)
        return "NULL_PATH"


def generatePreviewThumbs(path, hash, mediadir, amount=5, n_frames=30*10):
    vid_folder = os.path.join( get_video_media_dir(mediadir, hash), 'previewthumbs' )
    os.makedirs(vid_folder, exist_ok=True)
    return media_generator.extractPreviewThumbs(path, vid_folder, amount=amount, resolution=[360, 1080], n_frames=n_frames)



def link_custom_thumbs(videos_dict: dict[str, dict], custom_thumbs_dir: str) -> dict[str, dict]:
    """ Connects *unconnected* custom thumbs to videos, adds to video object and renames thumbnail """
    fn_to_hash = { vid['filename']: hash for hash, vid in videos_dict.items() }
    connected_suffix = 'CONN '
    unlinked_custom_thumbs = [ t for t in os.listdir(custom_thumbs_dir) if not t.startswith(connected_suffix) ]
    for i, thumb in enumerate(unlinked_custom_thumbs):
        print('  ({}/{}) thumb: "{}"'.format(i+1, len(unlinked_custom_thumbs), thumb))
        thumb_obj = Path(thumb)
        linked = False
        for fn in fn_to_hash.keys():
            if thumb_obj.stem.lower() in fn.lower():
                hash = fn_to_hash[fn]
                newname = '{}{} [{}]{}'.format(connected_suffix, thumb_obj.stem, hash, thumb_obj.suffix)
                old_path = os.path.join(custom_thumbs_dir, thumb)
                new_path = os.path.join(custom_thumbs_dir, newname)
                os.rename(old_path, new_path)
                videos_dict[hash]['custom_thumb'] = new_path
                print('Linked to video!\n:"{}"'.format(videos_dict[hash]['path']))
                linked = True
                break
        if not linked:
            print('Failed to link: "{}"'.format(thumb))
    return videos_dict




