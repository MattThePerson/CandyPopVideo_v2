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
from datetime import datetime

from handymatt_media import media_generator

from ..schemas import VideoData


#region ### CHECKERS ###

def hasPoster(video_hash: str, mediadir: str) -> str|None:
    """ For given hash, returns poster relative path if exists """
    poster_path = os.path.join( _get_video_media_dir(mediadir, video_hash), 'poster.png' )
    if not os.path.exists(poster_path):
        return None
    return 'poster.png' #_path_relative_to(poster_path, mediadir)


# DEPRECATED
def hasSeekThumbs(video_hash: str, mediadir: str):
    """ checks if seekthumbs.jpg and seekthumbs.vtt exist in video preview media dir """
    videomediadir = _get_video_media_dir(video_hash, mediadir)
    return os.path.exists( videomediadir + '/seekthumbs.jpg') and os.path.exists( videomediadir + '/seekthumbs.vtt' )


def hasTeaserSmall(video_hash: str, mediadir: str) -> bool:
    if hash == -1:
        input("\n\nMINUS ONE")
    teaser_small_path = os.path.join( _get_video_media_dir(mediadir, video_hash), 'teaser_small.mp4' )
    return os.path.exists(teaser_small_path)


def hasTeaserLarge(hash, mediadir):
    teaser_large_path = os.path.join( _get_video_media_dir(mediadir, hash), 'teaser_large.mp4' )
    return os.path.exists(teaser_large_path)


def hasPreviewThumbs(hash, mediadir, small=True):
    vid_folder = f'{_get_video_media_dir(mediadir, hash)}/previewthumbs'
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



#region ### GENERATORS ###

def generatePosterSimple(video_path: str, video_hash: str, mediadir: str, duration_sec: float) -> str|None:
    """ For given video path and hash, generates simple poster into mediadir and returns poster relative path """
    if not os.path.exists(video_path):
        raise FileNotFoundError("Video path doesn't exist:", video_path)
    poster_path = f'{_get_video_media_dir(mediadir, video_hash)}/poster.png'
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



# DEPRECATED!
def generateSeekThumbs_ffmpeg(videopath: str, video_hash: str, mediadir: str, duration_sec: float, height=180):
    """ Uses ffmpeg to generate seek thumbnails (HUOM: Doesn't generate spritesheet) """
    if not os.path.exists(videopath):
        print("Video doesn't exits:", videopath)
        return False
    seekthumbsdir = os.path.join(_get_video_media_dir(mediadir, video_hash), 'seekthumbs')
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


def generateTeaserSmall(path, hash, mediadir, duration_sec, quiet=True):
    outfolder = _get_video_media_dir(mediadir, hash)
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
        return "NULL_PATH"


def generateTeaserLarge(path, hash, mediadir, duration_sec):
    outfolder = _get_video_media_dir(mediadir, hash)
    if not os.path.exists(outfolder):
        print("Making folder: ", outfolder)
        os.makedirs(outfolder)
    clip_amount = int( ( 584/119 + (11/5355)*duration_sec ) * 2 )
    return media_generator.generateVideoTeaser(path, outfolder, 'teaser_large.mp4', abs_amount_mode=True, n=clip_amount, clip_len=1.65, skip=1, smallSize=False, end_perc=98)


def generatePreviewThumbs(path, hash, mediadir, amount=5, n_frames=30*10):
    vid_folder = os.path.join( _get_video_media_dir(mediadir, hash), 'previewthumbs' )
    os.makedirs(vid_folder, exist_ok=True)
    paths = media_generator.extractPreviewThumbs(path, vid_folder, amount=amount, resolution=[360, 1080], n_frames=n_frames)




#region ### MASS GEN ###


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


def generateSeekThumbnailsForVideos(videos_list: list[VideoData], mediadir):
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        if not hasSeekThumbs(video_data.hash, mediadir):
            print("\r  ({}/{}) generating seek thumbs  {:<80}    ".format(i+1, len(videos_list), f"{video_data.path[:76]}"), end='')
            vid_media_dir = _get_video_media_dir(mediadir, video_data.hash)
            media_generator.generateSeekThumbnails(video_data.path, vid_media_dir)
            # generateSeekThumbs(vd['path'], video_data.hash, mediadir, vd['duration_seconds'])


def generatePreviewThumbnailsForVideos(videos, mediadir, redo=False, n_frames=30*10):
    succ, fails = [], []
    for i, vd in enumerate(videos):
        hash = vd['hash']
        if redo or not hasPreviewThumbs(hash, mediadir, small=True):
            print("\r  ({}/{}) generating preview thumbnails [{}]  {:<80}    ".format(i+1, len(videos), hash, f"{vd['path'][:76]}"), end='')
            generatePreviewThumbs(vd['path'], hash, mediadir, amount=5, n_frames=n_frames)




#region ### MISC ###

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




#region ### HELPERS ###


def _get_video_media_dir(mediadir: str, video_hash: str) -> str:
    """ gets path to videos media directory {mediadir}/videos/0x{videohash}/"""
    return f'{mediadir}/0x{video_hash}'



def _path_relative_to(path: str, dirpath: str) -> str:
    return str(Path(path).relative_to(Path(dirpath)))

def _confirm_file_parent_exists(path: str):
    if os.path.isfile(path):
        path = os.path.dirname(path)
    os.makedirs(path, exist_ok=True)

