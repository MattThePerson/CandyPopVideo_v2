# command line: uvicorn main:app --workers 1 --port 8000
# production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
from fastapi import FastAPI, Response, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from config import PREVIEW_MEDIA_DIR
from app.routers import api_router, media_router, query_router, dashboard_router, interact_router



# Startup/Shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ...
    except KeyboardInterrupt:
        print('\n... keyboard interrupt. stopping scan.')
    
    yield
    print('FastAPI shutting down ...')


# CORS
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
app.add_middleware(NoCacheMiddleware)

# add routers
app.include_router(media_router,         prefix="/media")
app.include_router(api_router,           prefix="/api")
app.include_router(query_router,         prefix="/api/query")
app.include_router(interact_router,      prefix="/api/interact")
app.include_router(dashboard_router,     prefix="")

# hello
@app.get("/api/hello")
def api_hello():
    return Response('I hearr ya', 200)

# port
@app.get("/api/get-port")
def get_port(request: Request):
    return {'port': request.url.port}

# static folder: preview media
app.mount("/static/preview-media", StaticFiles(directory=PREVIEW_MEDIA_DIR), name="preview-media")


app.mount("/", StaticFiles(directory="frontend", html=True), name="")


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
