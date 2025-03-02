""" Functions for getting/changing data in db """
import os

from handymatt.sqlite_api import MySQLiteApi

from config import APP_DATA_DIR

_videos_db_path = os.path.join( APP_DATA_DIR, 'videos.db' )
_videos_db = MySQLiteApi(_videos_db_path)



def getVideosInDb():
    ...


def getVideoFromDb(video_hash: str):
    ...




def _initDb():
    ...

