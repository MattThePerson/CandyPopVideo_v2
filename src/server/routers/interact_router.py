from datetime import datetime
from fastapi import APIRouter, HTTPException
from datetime import datetime

from src.util import db
from src.util.config import DATETIME_FORMAT
from src.schemas import VideoInteractions


def get_video_interactions(video_hash: str):
    interactions = db.read_table_as_dict('interactions')
    video_interact_dict = interactions.get(video_hash, {})
    video_interact_dict['hash'] = video_hash
    return VideoInteractions.from_dict(video_interact_dict)
    

interact_router = APIRouter()


@interact_router.get('/get/{video_hash}')
def ROUTE_get(video_hash: str):
    video_interactions = get_video_interactions(video_hash)
    return video_interactions.to_dict()


# FAVOURITES

@interact_router.post("/favourites/add/{video_hash}")
def ROUTE_add_favourite(video_hash: str):
    video_interactions = get_video_interactions(video_hash)
    if video_interactions.is_favourite:
        raise HTTPException(status_code=400, detail="Video is already favourite")
    video_interactions.is_favourite = True
    video_interactions.favourited_date = datetime.now().strftime(DATETIME_FORMAT)
    print('Adding favourite!!')
    db.write_object_to_db(video_hash, video_interactions.to_dict(), 'interactions')
    return { 'msg': 'favourite added' }


@interact_router.post("/favourites/remove/{video_hash}")
def ROUTE_remove_favourite(video_hash: str):
    video_interactions = get_video_interactions(video_hash)
    if not video_interactions.is_favourite:
        raise HTTPException(status_code=400, detail="Video is already NOT a favourite")
    video_interactions.is_favourite = False
    video_interactions.favourited_date = None
    # video_interactions.favourited_date = datetime.now().strftime(DATETIME_FORMAT)
    db.write_object_to_db(video_hash, video_interactions.to_dict(), 'interactions')
    return { 'msg': 'favourite removed' }


@interact_router.get("/favourites/check/{video_hash}")
def ROUTE_is_favourite(video_hash: str):
    vid_inter = get_video_interactions(video_hash)
    return { 'is_favourite': vid_inter.is_favourite }



# RATINGS

@interact_router.post("/rating/update/{video_hash}")
def ROUTE_update_rating(video_hash: str):
    ...


@interact_router.post("/rating/get/{video_hash}")
def ROUTE_get_rating(video_hash: str):
    ...



# LIKES

@interact_router.post("/likes/add/{video_hash}")
def ROUTE_likes_add(video_hash: str):
    vid_inter = get_video_interactions(video_hash)
    vid_inter.likes += 1
    db.write_object_to_db(video_hash, vid_inter.to_dict(), 'interactions')
    return { 'likes': vid_inter.likes }


@interact_router.get("/likes/get/{video_hash}")
def ROUTE_likes_get(video_hash: str):
    ...



# VIEWS

@interact_router.post("/last-viewed/add/{video_hash}")
def ROUTE_add_last_viewed(video_hash: str):
    vid_inter = get_video_interactions(video_hash)
    vid_inter.last_viewed = str(datetime.now())
    db.write_object_to_db(video_hash, vid_inter.to_dict(), 'interactions')
    return { 'msg': 'added view' }


@interact_router.post("/viewtime/add/{video_hash}/{viewtime}")
def ROUTE_add_viewtime(video_hash: str, viewtime: float):
    vid_inter = get_video_interactions(video_hash)
    vid_inter.viewtime += viewtime
    db.write_object_to_db(video_hash, vid_inter.to_dict(), 'interactions')
    db.write_to_table({
        "timestamp": str(datetime.now())[:-7].replace(' ', 'T'),
        'video_hash': video_hash,
        'duration_sec': viewtime,
    }, 'views')
    return { 'msg': 'added view time' }


# MARKERS

@interact_router.post("/markers/update/{video_hash}")
def ROUTE_add_markers(video_hash: str):
    ...


@interact_router.get("/markers/get/{video_hash}")
def ROUTE_get_markers(video_hash: str):
    ...





