import os
from pathlib import Path
from argparse import Namespace

from handymatt_media import media_generator

from ..schemas import VideoData
from ..media import generators, checkers
from ..media.helpers import get_video_media_dir
from .helpers import aprint
from ..loggers import MEDIA_GEN_FAILED



async def mass_generate_small_teasers(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'small_teasers'
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        await aprint(ws, "\r  ({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :"
                    .format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] ), end='')
        if not checkers.hasSeekThumbs(video_data.hash, mediadir) or redo:
            print()
            media_path = ""
            try:
                # START GENERATOR
                media_path = generators.generateTeaserSmall(video_data.path, video_data.hash, mediadir, video_data.duration_seconds)
                # END GENERATOR
            except Exception as e:
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} EXCEPTION [{}] "{}"\n{}'.format(type_, video_data.hash, video_data.path, e))
            if media_path is None or not os.path.exists(media_path):
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} [{}] "{}"'.format(type_, video_data.hash, video_data.path))
            else:
                succ.append(video_data.path)
            if limit and (len(succ) + len(fails)) >= limit:
                break
    await aprint(ws, '\nDone.')
    return succ, fails


async def mass_generate_seek_thumbs(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'seek_thumbs'
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        await aprint(ws, "\r  ({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :"
                    .format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] ), end='')
        if not checkers.hasSeekThumbs(video_data.hash, mediadir) or redo:
            print()
            media_path = ""
            try:
                # START GENERATOR
                vid_media_dir = get_video_media_dir(mediadir, video_data.hash)
                spritesheet_path, _ = media_generator.generateSeekThumbnails( video_data.path, vid_media_dir, n=400, height=300 )
                media_path = spritesheet_path
                # END GENERATOR
            except Exception as e:
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} EXCEPTION [{}] "{}"\n{}'.format(type_, video_data.hash, video_data.path, e))
            if media_path is None or not os.path.exists(media_path):
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} [{}] "{}"'.format(type_, video_data.hash, video_data.path))
            else:
                succ.append(video_data.path)
            if limit and (len(succ) + len(fails)) >= limit:
                break
    await aprint(ws, '\nDone.')
    return succ, fails


async def mass_generate_preview_thumbs(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, n_frames=30*10, ws=None):
    type_ = 'preview_thumbs'
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        await aprint(ws, "\r  ({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :"
                    .format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] ), end='')
        if not checkers.hasSeekThumbs(video_data.hash, mediadir) or redo:
            print()
            media_path = ""
            try:
                # START GENERATOR
                thumbs = generators.generatePreviewThumbs(video_data.path, video_data.hash, mediadir, amount=5, n_frames=n_frames)
                if thumbs and thumbs != []:
                    media_path = thumbs[0]
                # END GENERATOR
            except Exception as e:
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} EXCEPTION [{}] "{}"\n{}'.format(type_, video_data.hash, video_data.path, e))
            if media_path is None or not os.path.exists(media_path):
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} [{}] "{}"'.format(type_, video_data.hash, video_data.path))
            else:
                succ.append(video_data.path)
            if limit and (len(succ) + len(fails)) >= limit:
                break
    await aprint(ws, '\nDone.')
    return succ, fails



async def mass_generate_large_teasers_OLD(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'large_teasers'
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        await aprint(ws, "\r  ({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :"
                    .format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] ), end='')
        if not checkers.hasSeekThumbs(video_data.hash, mediadir) or redo:
            print()
            media_path = ""
            try:
                # START GENERATOR
                media_path = generators.generateTeaserLarge(video_data.path, video_data.hash, mediadir, video_data.duration_seconds)
                # END GENERATOR
            except Exception as e:
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} EXCEPTION [{}] "{}"\n{}'.format(type_, video_data.hash, video_data.path, e))
            if media_path is None or not os.path.exists(media_path):
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} [{}] "{}"'.format(type_, video_data.hash, video_data.path))
            else:
                succ.append(video_data.path)
            if limit and (len(succ) + len(fails)) >= limit:
                break
    await aprint(ws, '\nDone.')
    return succ, fails



async def mass_generate_teaser_thumbs(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'teaser_thumbs'
    succ, fails = [], []
    for i, video_data in enumerate(videos_list):
        await aprint(ws, "\r  ({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :"
                    .format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] ), end='')
        if not checkers.hasSeekThumbs(video_data.hash, mediadir) or redo:
            print()
            media_path = ""
            try:
                # START GENERATOR
                ...
                # END GENERATOR
            except Exception as e:
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} EXCEPTION [{}] "{}"\n{}'.format(type_, video_data.hash, video_data.path, e))
            if media_path is None or not os.path.exists(media_path):
                fails.append(video_data.path)
                MEDIA_GEN_FAILED.error('{} [{}] "{}"'.format(type_, video_data.hash, video_data.path))
            else:
                succ.append(video_data.path)
            if limit and (len(succ) + len(fails)) >= limit:
                break
    await aprint(ws, '\nDone.')
    return succ, fails
