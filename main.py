# command line: uvicorn main:app --workers 1 --port 8000
# production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from backend.routers import api_router, media_router, query_router, dashboard_router
from config import PREVIEW_MEDIA_DIR, COLLECTIONS



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
app.include_router(media_router,     prefix="/media")
app.include_router(api_router,       prefix="/api")
app.include_router(query_router,     prefix="/api/query")
app.include_router(dashboard_router, prefix="/api/dashboard")

# test
@api_router.get("/api/hello")
def read_root():
    return Response('I hearr ya', 200)

# static folder: preview media
app.mount("/static/preview-media", StaticFiles(directory=PREVIEW_MEDIA_DIR), name="preview-media")


# [DEV] Determine which frontend to serve
import os
if os.getenv("USE_OLD_FRONTEND") == "1":
    print('[PYTHON] Mounting "frontend"')
    app.mount("/", StaticFiles(directory="frontend", html=True), name="old")
else:
    print('[PYTHON] Mounting "frontend_svelte/build"')
    app.mount("/", StaticFiles(directory="frontend_svelte/build", html=True), name="new")



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
