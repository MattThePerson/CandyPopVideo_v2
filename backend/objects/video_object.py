""" Contains dataclass for containing video data """
from dataclasses import dataclass


@dataclass
class VideoObject:
    """ Dataclass for containing video data """
    
    hash: str
    path: str
    filename: str
    parent_dir: str
    path_relative: str
    date_added: str
    
    # video attributes
    duration: str
    duration_seconds: float
    filesize_mb: float
    fps: float
    resolution: int
    bitrate: int
    
    # scene attributes
    title: str
    date_released: str
    performers: list[str]
    sort_performers: list[str]
    mention_performers: list[str]
    studio: str
    
    # meta
    collection: str
    tags: list[str]
    tags_from_filename: list[str]
    tags_from_path: list[str]
    tags_from_json: list[str]
    
    # OPTIONAL
    line: str|None = None
    

# obj = VideoObject(
    
# )