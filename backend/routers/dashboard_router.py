from fastapi import APIRouter, Response, HTTPException

from handymatt.wsl_paths import convert_to_wsl_path, convert_to_windows_path

from ..util import media


dashboard_router = APIRouter()

@dashboard_router.get("/scan-videos")
def DASHBOARD_scanVideos():
    raise HTTPException(501, 'Not implemented')
    ...
    
    return {"message": "Hello there!"}


@dashboard_router.get("/generate-media/")
def DASHBOARD_():
    ...

