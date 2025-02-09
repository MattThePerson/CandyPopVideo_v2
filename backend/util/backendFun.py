import os
import time
import random
from datetime import datetime

from handymatt_media.media_generator import media_generator


# TODO: Remove (DEPRECATED!)
# Makes thumbs.vtt file given interval and scale parameters
# Assumes that thumbs exist in subfolder called 'seekthumbs'
def makeThumbsVTTFile(thumbsdir, filepath, interval_sec, scale_x, scale_y, tile, path_start='', save_to_thumbs_dir=False):
    if save_to_thumbs_dir:
        filepath = os.path.join( thumbsdir, filepath )
    if not os.path.exists(thumbsdir):
        print("ERROR (makeThumbsVTTFile): Seekthumbs dir does not exist")
        return False
    file = open(filepath, 'w')
    file.write("WEBVTT\n\n\n")

    count = 0
    for tn in os.listdir(thumbsdir):
        if tn.endswith("jpg") or tn.endswith("png"):
            tnpath = "{}/{}".format(path_start, tn)
            for j in range(tile[1]):
                for i in range(tile[0]):
                    time_start = time.strftime("%H:%M:%S.000", time.gmtime( (count) * interval_sec ))
                    time_end   = time.strftime("%H:%M:%S.000", time.gmtime(   (count+1) * interval_sec ))
                    line_start = "{} --> {}\n{}".format(time_start, time_end, tnpath)
                    line_end = "{},{},{},{}".format(scale_x*i, scale_y*j, scale_x, scale_y)
                    line = "{}#xywh={}\n\n".format(line_start, line_end)
                    file.write(line)
                    count += 1
    file.close()
    return True


# 
def create_gif_random_time(video, gifsdir):
    start_perc, end_perc = 0.05, 0.9
    start_time_sec = int( int(video['duration_seconds']) * (random.random()*(end_perc-start_perc) + start_perc) )
    print(start_time_sec)
    savedir = os.path.join( gifsdir, video['hash'] )
    path = media_generator.create_gif(video['path'], savedir, start_time_sec)
    return path



#### FAVOURITES FUNCTIONS ####

def add_favourite(hash, metadataHandler):
    favourites = metadataHandler.getValue('favourites')
    if favourites == None:
        favourites = []
    if not hash in favourites:
        favourites.append(hash)
    metadataHandler.setValue('favourites', favourites)

def remove_favourite(hash, metadataHandler):
    favourites = metadataHandler.getValue('favourites')
    if favourites == None:
        favourites = []
        return
    if hash in favourites:
        favourites.remove(hash)
    metadataHandler.setValue('favourites', favourites)

def is_favourite(hash, metadataHandler):
    favourites = metadataHandler.getValue('favourites')
    if favourites == None:
        return False
    return hash in favourites

