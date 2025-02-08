# production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from backend.fastapi_routers import router
from backend.app_state import AppState

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

# MAIN

state = AppState()
state.load(
    _data_dir,
    quick_start = False,
)
print(len(state.videos_dict))
input('...')

app = FastAPI()
app.add_middleware(NoCacheMiddleware)

app.include_router(router, prefix="/api")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


