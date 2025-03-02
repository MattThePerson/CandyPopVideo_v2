# command line: uvicorn main:app --workers 1
# production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
import os
import sys
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from handymatt.wsl_paths import convert_to_wsl_path

from backend.routes import api_router, api_media_router, search_router, dashboard_router
from config import PREVIEW_MEDIA_DIR



# region global variables

_project_dir = os.path.dirname(__file__)
_data_dir = os.path.join( _project_dir, 'data' )


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.endswith((".html", ".js", ".css")):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

#region State

try:
    # scanVideos()
    ...
except KeyboardInterrupt:
    print('\n\n... caught Keyboard Interrupt during state load')
    sys.exit(0)


#region FastAPI

app = FastAPI()
app.add_middleware(NoCacheMiddleware) # TODO: test removing

# add routers
app.include_router(api_router, prefix="/api")
app.include_router(api_media_router, prefix="/api/media")
app.include_router(search_router, prefix="/search")
app.include_router(dashboard_router, prefix="/dashboard")

# TODO: Move to base_router.py
# videos route
@app.get('/video/{video_hash}')
def xyz(video_hash: str):
    # data = state.videos_dict.get(video_hash)
    data = None
    if data is None:
        return Response(f'Data not found for hash {video_hash}', 404)
    video_path = convert_to_wsl_path(data.path)
    print('video_hash:', video_hash)
    print('video_path', video_path)
    if not os.path.exists(video_path):
        return Response(f'Video path doesnt exist "{video_path}"', 404)
    return FileResponse(video_path, media_type='video/mp4')

# static (preview) media
app.mount("/media", StaticFiles(directory=PREVIEW_MEDIA_DIR), name="media")

# frontend
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
# app.mount("/", StaticFiles(directory="frontend_old", html=True), name="frontend")


#region START
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
