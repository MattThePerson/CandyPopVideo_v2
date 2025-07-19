""" Contains dataclass for containing video data """
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class VideoData:
    """ Dataclass for containing video data """
    
    hash: str
    date_added: str # eg. 2025-06-12 20:00
    path: str
    filename: str
    
    # video attributes
    duration: str
    filesize_mb: float
    fps: float
    resolution: int
    bitrate: int
    duration_seconds: float

    source_id:      Optional[str] = None
    # source_url:     Optional[str] = None

    # collection
    collection:     Optional[str] = None
    parent_dir:     Optional[str] = None
    path_relative:  Optional[str] = None
    
    # scene attributes
    title:              Optional[str] = None
    scene_title:        Optional[str] = None
    scene_number:       Optional[int] = None
    movie_title:        Optional[str] = None
    movie_series:       Optional[str] = None
    
    studio:             Optional[str] = None
    line:               Optional[str] = None
    date_released:      Optional[str] = None
    description:        Optional[str] = None
    dvd_code:           Optional[str] = None
    # d18_url:            Optional[str] = None
    # date_released_d18:  Optional[str] = None
    
    actors:                 list[str] = field(default_factory=list)
    primary_actors:         list[str] = field(default_factory=list)
    secondary_actors:       list[str] = field(default_factory=list)
    
    # meta
    tags:               list[str] = field(default_factory=list)
    tags_from_filename: list[str] = field(default_factory=list)
    tags_from_path:     list[str] = field(default_factory=list)
    tags_from_json:     list[str] = field(default_factory=list)
    genres:             list[str] = field(default_factory=list)
    # tags_from_d18:      list[str] = field(default_factory=list)
    metadata:                dict = field(default_factory=dict)
    
    is_linked:               bool = True


    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data, strict=True):
        if strict:
            return cls(**data)  # Will fail if extra attributes exist
        else:
            valid_keys = { field.name for field in cls.__dataclass_fields__.values() }
            filtered_data = { k: v for k, v in data.items() if k in valid_keys }
            return cls(**filtered_data)
