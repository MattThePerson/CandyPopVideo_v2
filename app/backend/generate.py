import os
from argparse import Namespace

from handymatt_media import media_generator

from ..schemas import VideoData
from ..media import generators, checkers
from ..media.helpers import get_video_media_dir
from .helpers import aprint



#region generators

async def mass_generate_small_teasers(videos: list[VideoData], mediadir, redo=False, ws=None):
    succ, fails = [], []
    for i, video_data in enumerate(videos):
        await aprint(ws, "\r  ({}/{}) generating small teasers ({} fails) [{}] {:<120}     ".format( i+1, len(videos), len(fails), video_data.hash, f"{video_data.path[:118]}" ), end='')
        if video_data.hash != -1 and (redo or not checkers.hasTeaserSmall(video_data.hash, mediadir)):
            teaser_path = generators.generateTeaserSmall(video_data.path, video_data.hash, mediadir, video_data.duration_seconds)
            if teaser_path == None or not os.path.exists(teaser_path):
                fails.append(video_data)
            else:
                succ.append(video_data)


async def mass_generate_seek_thumbs(videos_list: list[VideoData], mediadir: str, redo=False, ws=None):
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        if not checkers.hasSeekThumbs(video_data.hash, mediadir):
            await aprint(ws, "\r  ({}/{}) generating seek thumbs  {:<80}    ".format(i+1, len(videos_list), f"{video_data.path[:76]}"), end='')
            vid_media_dir = get_video_media_dir(mediadir, video_data.hash)
            media_generator.generateSeekThumbnails(video_data.path, vid_media_dir)
            # generateSeekThumbs(vd['path'], video_data.hash, mediadir, vd['duration_seconds'])
    ...


async def mass_generate_preview_thumbs(videos: list[VideoData], mediadir, redo=False, n_frames=30*10, ws=None):
    succ, fails = [], []
    for i, video_data in enumerate(videos):
        if redo or not checkers.hasPreviewThumbs(video_data.hash, mediadir, small=True):
            await aprint(ws, "\r  ({}/{}) generating preview thumbnails [{}]  {:<80}    ".format(i+1, len(videos), video_data.hash, f"{video_data.path[:76]}"), end='')
            generators.generatePreviewThumbs(video_data.path, video_data.hash, mediadir, amount=5, n_frames=n_frames)
    ...



async def mass_generate_large_teasers(videos: list[VideoData], mediadir: str, redo=False, ws=None):
    ...
    
async def mass_generate_teaser_thumbs(videos: list[VideoData], mediadir: str, redo=False, ws=None):
    ...
    
