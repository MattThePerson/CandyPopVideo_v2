""" Contains dataclass for containing video data """
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
# field(default_factory=list) prevents [] being a mutable default argument 
class VideoInteractions:
    """ Dataclass for containing video interactions """
    
    hash:         str
    
    last_viewed:        str|None = None # basically last played
    viewtime:           float = 0

    is_favourite:       bool = False
    favourited_date:    str|None = None
    
    views:          list[str] = field(default_factory=list) # list of dates
    likes:          int = 0
    rating:         str|None = None  # S+ | S | A | B+ | B- | C
    
    markers:        list[tuple] = field(default_factory=list) # ( video_time, color, tag )
    dated_markers:  list[tuple] = field(default_factory=list) # ( video_time, datetime )
    comments:       list[tuple] = field(default_factory=list) # ( comment, datetime )
    
    
    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data, strict=True):
        if strict:
            return cls(**data)  # Will fail if extra attributes exist
        else:
            valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            return cls(**filtered_data)
