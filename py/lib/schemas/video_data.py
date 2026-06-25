from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class VideoData:
    hash: str
    date_added: str
    path: str
    filename: str

    duration: str
    filesize_mb: float
    fps: float
    height: int
    bitrate: int
    duration_seconds: float

    width: int = 0
    resolution: str = ""
    aspect_ratio: str = ""
    is_vfr: bool = False
    video_codec: str = ""
    audio_codec: str = ""
    pix_fmt: str = ""
    color_transfer: str = ""

    source_id:      Optional[str] = None

    collection:     Optional[str] = None
    parent_dir:     Optional[str] = None
    path_relative:  Optional[str] = None

    title:              Optional[str] = None
    scene_title:        Optional[str] = None
    scene_number:       Optional[int] = None
    movie_title:        Optional[str] = None
    movie_series:       Optional[str] = None

    studio:             Optional[str] = None
    line:               Optional[str] = None
    date_released:      Optional[str] = None
    description:        str = ""
    dvd_code:           Optional[str] = None

    actors:                 list[str] = field(default_factory=list)
    primary_actors:         list[str] = field(default_factory=list)
    secondary_actors:       list[str] = field(default_factory=list)

    tags:               list[str] = field(default_factory=list)
    tags_from_filename: list[str] = field(default_factory=list)
    tags_from_path:     list[str] = field(default_factory=list)
    tags_from_json:     list[str] = field(default_factory=list)
    genres:             list[str] = field(default_factory=list)
    metadata:                dict = field(default_factory=dict)

    views:  Optional[int] = None
    rating: Optional[float] = None
    likes:  Optional[int] = None

    is_linked: bool = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data, strict=True):
        if strict:
            return cls(**data)
        else:
            valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            return cls(**filtered_data)
