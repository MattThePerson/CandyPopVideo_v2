""" Contains dataclass for containing video data """
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class VideoData:
    """ Dataclass for containing video data """
    
    hash: str
    date_added: str
    path: str
    
    # video attributes
    duration: str
    filesize_mb: float
    fps: float
    resolution: int
    bitrate: int
    duration_seconds: float

    filename:       Optional[str] = None
    source_id:      Optional[str] = None

    # collection
    collection:     Optional[str] = None
    parent_dir:     Optional[str] = None
    path_relative:  Optional[str] = None
    
    # scene attributes
    scene_title:    Optional[str] = None
    studio:         Optional[str] = None
    line:           Optional[str] = None
    date_released:  Optional[str] = None
    description:    Optional[str] = None
    jav_code:       Optional[str] = None
    performers:         list[str] = field(default_factory=list)
    sort_performers:    list[str] = field(default_factory=list)
    mention_performers: list[str] = field(default_factory=list)
    
    # meta
    tags:               list[str] = field(default_factory=list)
    tags_from_filename: list[str] = field(default_factory=list)
    tags_from_path:     list[str] = field(default_factory=list)
    tags_from_json:     list[str] = field(default_factory=list)
    metadata:           dict = field(default_factory=dict)

