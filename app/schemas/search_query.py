from pydantic import BaseModel


class SearchQuery(BaseModel):
    search_string:      str|None
    performer:          str|None
    studio:             str|None
    collection:         str|None
    include_terms:      list[str]
    exclude_terms:      list[str]
    date_added_from:        str|None
    date_added_to:          str|None
    date_released_from:     str|None
    date_released_to:       str|None
    only_favourites:    bool
    sortby:             str|None
    limit:              int
    startfrom:          int
