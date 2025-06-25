# command line: uvicorn main:app --workers 1
# production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
import os
import sys
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from handymatt.wsl_paths import convert_to_wsl_path

from backend.routers import api_router, ensure_media_router, query_router, dashboard_router
from backend.util.load import scanVideos
from config import PREVIEW_MEDIA_DIR, COLLECTIONS

# from backend.schemas.video_data import VideoData


# global variables

_project_dir = os.path.dirname(__file__)
_data_dir = os.path.join( _project_dir, 'data' )


# Startup/Shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    try:
        # print('Scanning media libraries ...')
        # scanVideos(COLLECTIONS)
        ...
    except KeyboardInterrupt:
        print('\n... keyboard interrupt. stopping scan.')
    
    yield
    print('FastAPI shutting down ...')


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.endswith((".html", ".js", ".css")):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


# FastAPI

app = FastAPI(lifespan=lifespan)
app.add_middleware(NoCacheMiddleware) # TODO: test removing

# add routers
app.include_router(api_router, prefix="/api")
app.include_router(ensure_media_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


# test
@api_router.get("/api/hello")
def read_root():
    return Response('I hearr ya', 200)


# TODO: Move to base_router.py
# videos route
@app.get('/media/video/{video_hash}')
def xyz(video_hash: str):
    # data = state.videos_dict.get(video_hash)
    print('finding video with hash:', video_hash)

    import json
    with open('data/videos.json', 'r') as f:
        videos_dict = json.load(f)
    print('Loaded dict of size:', len(videos_dict))
    data = videos_dict.get(video_hash)
    
    if data is None:
        return Response(f'Data not found for hash {video_hash}', 404)
    video_path = convert_to_wsl_path(data['path'])
    print('video_hash:', video_hash)
    print('video_path', video_path)
    if not os.path.exists(video_path):
        return Response(f'Video path doesnt exist "{video_path}"', 404)
    return FileResponse(video_path, media_type='video/mp4')


# static (preview) media
app.mount("/media/static", StaticFiles(directory=PREVIEW_MEDIA_DIR), name="media")


# frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")



# START
if __name__ == '__main__':
    import uvicorn
    print('Starting uvicorn')
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        workers=1,
        reload=False
    )
