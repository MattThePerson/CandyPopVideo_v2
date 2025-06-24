from fastapi import APIRouter, Response, Depends

from handymatt.wsl_paths import convert_to_wsl_path, convert_to_windows_path

from ..util import media


dashboard_router = APIRouter()

@dashboard_router.get("/dashboard/scan-videos")
def DASHBOARD_scanVideos():
    return Response('Not implemented', 501)
    ...
    
    return {"message": "Hello there!"}


@dashboard_router.get("/dashboard/generate-media/")
def DASHBOARD_():
    ...

