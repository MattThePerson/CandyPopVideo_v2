import os
from pathlib import Path
from argparse import Namespace
import time
import gc

from handymatt_media import media_generator

from ..schemas import VideoData
from ..media import generators, checkers
# from ..media.helpers import get_video_media_dir
from .helpers import aprint
from ..loggers import MEDIA_GEN, MEDIA_GEN_FAILED


def mass_generate_preview_thumbs(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, n_frames=30*10, ws=None):
    type_ = 'preview_thumbs'
    succ, fails = [], []
    try:
        for i, video_data in enumerate(videos_list):
            info_msg = "({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :".format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] )
            MEDIA_GEN.info(info_msg)
            print("\r  {}".format(info_msg), end='')
            if not checkers.hasPreviewThumbs(video_data.hash, mediadir) or redo:
                print()
                media_path = ""
                try:
                    # START GENERATOR
                    thumbs = generatePreviewThumbs(
                        video_data.path,
                        video_data.hash,
                        mediadir,
                        amount=5,
                        n_frames=n_frames,
                    )
                    if thumbs and thumbs != []:
                        media_path = thumbs[0]
                    # END GENERATOR
                except Exception as e:
                    fails.append(video_data.path)
                    MEDIA_GEN_FAILED.error('{} EXCEPTION [{}] "{}"\n{}'.format(type_, video_data.hash, video_data.path, e))
                if media_path is None or not os.path.exists(media_path):
                    fails.append(video_data.path)
                    MEDIA_GEN_FAILED.error('{} no generated media [{}] "{}"'.format(type_, video_data.hash, video_data.path))
                else:
                    succ.append(video_data.path)
                if limit and (len(succ) + len(fails)) >= limit:
                    break
    except KeyboardInterrupt:
        print('\n  ... interrupting')
    print('\nDone.')
    return succ, fails



def mass_generate_seek_thumbs(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'seek_thumbs'
    succ, fails = [], []
    try:
        for i, video_data in enumerate(videos_list):
            info_msg = "({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :".format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] )
            MEDIA_GEN.info(info_msg)
            print("\r  {}".format(info_msg), end='')
            if not checkers.hasSeekThumbs(video_data.hash, mediadir) or redo:
                print()
                media_path = ""
                try:
                    # START GENERATOR
                    vid_media_dir = checkers.get_video_media_dir(mediadir, video_data.hash)
                    spritesheet_path, _ = media_generator.generateVideoSpritesheet(
                        video_data.path,
                        vid_media_dir,
                        number_of_frames=400,
                        height=300,
                        filestem='seekthumbs',
                    )
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
    except KeyboardInterrupt:
        print('\n  ... interrupting')
    print('\nDone.')
    return succ, fails




def mass_generate_teasers_small(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'small_teasers'
    succ, fails = [], []
    try:
        for i, video_data in enumerate(videos_list):
            info_msg = "({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :".format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] )
            MEDIA_GEN.info(info_msg)
            print("\r  {}".format(info_msg), end='')
            if not checkers.hasTeaserSmall(video_data.hash, mediadir) or redo:
                print()
                media_path = ""
                try:
                    # START GENERATOR
                    media_path = generators.generateTeaserSmall(
                        video_data.path,
                        video_data.hash,
                        mediadir,
                        video_data.duration_seconds,
                    )
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
    except KeyboardInterrupt:
        print('\n  ... interrupting')
    print('\nDone.')
    return succ, fails



def mass_generate_teasers_large(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'large_teasers'
    succ, fails = [], []
    try:
        for i, video_data in enumerate(videos_list):
            info_msg = "({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :".format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] )
            MEDIA_GEN.info(info_msg)
            print("\r  {}".format(info_msg), end='')
            if not checkers.hasTeaserLarge(video_data.hash, mediadir) or redo:
                print()
                media_path = ""
                try:
                    # START GENERATOR
                    media_path = generators.generateTeaserLarge(
                        video_data.path,
                        video_data.hash,
                        mediadir,
                        video_data.duration_seconds,
                    )
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
    except KeyboardInterrupt:
        print('\n  ... interrupting')
    print('\nDone.')
    return succ, fails



def mass_generate_teaser_thumbs_small(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None, delay=3):
    type_ = 'teaser_thumbs'
    succ, fails = [], []
    try:
        for i, video_data in enumerate(videos_list):
            info_msg = "({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :".format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] )
            MEDIA_GEN.info(info_msg)
            print("\r  {}".format(info_msg), end='')
            if not checkers.hasTeaserThumbsSmall(video_data.hash, mediadir) or redo:
                print()
                media_path = ""
                try:
                    # START GENERATOR
                    vid_media_dir = checkers.get_video_media_dir(mediadir, video_data.hash)
                    spritesheet_path, _ = media_generator.generateVideoSpritesheet(
                        video_data.path,
                        vid_media_dir,
                        number_of_frames=16,
                        height=300,
                        filestem='teaser_thumbs_small',
                    )
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
                time.sleep(delay)
                gc.collect()
    except KeyboardInterrupt:
        print('\n  ... interrupting')
    print('\nDone.')
    return succ, fails



def mass_generate_teaser_thumbs_large(videos_list: list[VideoData], mediadir: str, redo=False, limit=None, ws=None):
    type_ = 'teaser_thumbs_large'
    succ, fails = [], []
    try:
        for i, video_data in enumerate(videos_list):
            info_msg = "({:_}/{:_}) generating {} (succ: {:_} | fails {:_})  [{}]  : {:<120} :".format( i+1, len(videos_list), type_, len(succ), len(fails), video_data.hash, Path(video_data.path).name[:118] )
            MEDIA_GEN.info(info_msg)
            print("\r  {}".format(info_msg), end='')
            if not checkers.hasTeaserThumbsLarge(video_data.hash, mediadir) or redo:
                print()
                media_path = ""
                try:
                    # START GENERATOR
                    vid_media_dir = checkers.get_video_media_dir(mediadir, video_data.hash)
                    spritesheet_path, _ = media_generator.generateVideoSpritesheet(
                        video_data.path,
                        vid_media_dir,
                        number_of_frames=30,
                        height=900,
                        filestem='teaser_thumbs_large',
                    )
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
    except KeyboardInterrupt:
        print('\n  ... interrupting')
    print('\nDone.')
    return succ, fails



#region - CHECKERS -----------------------------------------------------------------------------------------------------



def checkPreviewMediaStatus(videos_list: list[VideoData], mediadir: str, selection: str, print_without: int|None=None, ws=None):
    options = {
        'teaser_thumbs':        checkers.hasTeaserThumbsSmall,
        'teasers':              checkers.hasTeaserSmall,
        'seek_thumbs':          checkers.hasSeekThumbs,
        'preview_thumbs':       checkers.hasPreviewThumbs,
        # 'teasers_large':        checkers.hasTeaserLarge,
        # 'teaser_thumbs_large':  checkers.hasTeaserThumbsLarge,
    }
    # get & print status
    print('{:<20} | {:>6} | {:>8} | {:>8} | {}'.format('MEDIA TYPE', 'PERC', 'WITH', 'WITHOUT', 'TOTAL'))
    with_media_all, without_media_all = [], []
    for name, checker_func in options.items():
        if selection == 'all' or selection == name:
            with_media, without_media = [], []
            for video_data in videos_list:
                if checker_func(video_data.hash, mediadir):
                    with_media.append((video_data.hash, video_data.path))
                else:
                    without_media.append((video_data.hash, video_data.path))
            with_media_all.extend(with_media)
            without_media_all.extend(without_media)
            # print status
            msg = _get_status_line(name, with_media, without_media)
            print(msg)
            if print_without and without_media != []:
                print('    videos without:', name)
                for idx, (hash_, path) in enumerate(without_media):
                    print('{:>4} : [{}] "{}"'.format(idx, hash_, path))
                    if idx+1 >= print_without:
                        print('  ...')
                        break
    msg = _get_status_line('all', with_media_all, without_media_all)
    print(msg)
    print('')
        

def _get_status_line(name, with_, without):
    yes, no = len(with_), len(without)
    total = yes + no
    perc = -1
    if total > 0:
        perc = (yes / (total)) * 100
    perc_str = '{:.1f}%'.format(perc)
    return '{:<20} | {:>6} : {:>8_} : {:>8_} : {:>8_} |'.format(name, perc_str, yes, no, total)


# HELPER

def generatePreviewThumbs(path, hash, mediadir, amount=5, n_frames=30*10):
    vid_folder = os.path.join( checkers.get_video_media_dir(mediadir, hash), 'previewthumbs' )
    os.makedirs(vid_folder, exist_ok=True)
    return media_generator.extractPreviewThumbs(path, vid_folder, amount=amount, resolution=[360, 1080], n_frames=n_frames)

