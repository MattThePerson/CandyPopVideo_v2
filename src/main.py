# command line: uvicorn main:app --workers 1 --port 8000
# production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from src.util.config import PREVIEW_MEDIA_DIR, ACTOR_INFO_DIR
from src.server.routers import api_router, media_router, query_router, interact_router # dashboard_router



# Startup/Shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
    yield
    print('Running shutdown logic ...')
    import asyncio
    tasks = [ t for t in asyncio.all_tasks() if not t.done() ]
    print(f"Unfinished tasks at shutdown: {len(tasks)}")
    for idx, task in enumerate(tasks):
        print(f'\n  {idx+1}:')
        print(task)



# FastAPI

app = FastAPI(lifespan=lifespan)

if os.getenv("DEV_MODE") == "1":
    print('[main] DEV_MODE: Using NoCacheMiddleware')
    class NoCacheMiddleware(BaseHTTPMiddleware): # Prevent caching of html, js, css
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            if request.url.path.endswith((".html", ".js", ".css")):
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            return response
    app.add_middleware(NoCacheMiddleware)



# ROUTERS

app.include_router(media_router,         prefix="/media")
app.include_router(api_router,           prefix="/api")
app.include_router(query_router,         prefix="/api/query")
app.include_router(interact_router,      prefix="/api/interact")
# app.include_router(dashboard_router,     prefix="")


# hello
@app.get("/api/hello-there")
def api_hello():
    return { 'msg': 'General Kenobi!' }

# port
@app.get("/api/get-port")
def get_port(request: Request):
    return {'port': request.url.port}

# static folder: preview media
app.mount("/static/preview-media", StaticFiles(directory=PREVIEW_MEDIA_DIR), name="preview-media")
app.mount("/static/actor-store", StaticFiles(directory=ACTOR_INFO_DIR), name="actor-store")


app.mount("/", StaticFiles(directory="frontend", html=True), name="")


# RUNNING PYTHON FILE
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
