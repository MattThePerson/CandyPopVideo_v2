from fastapi import APIRouter, Response, Depends, HTTPException

from handymatt.wsl_paths import convert_to_wsl_path, convert_to_windows_path

from ..util import media


dashboard_router = APIRouter()

@dashboard_router.get("/scan_videos")
def dashboard_scanVideos():

    ...
    
    return {"message": "Hello there!"}

