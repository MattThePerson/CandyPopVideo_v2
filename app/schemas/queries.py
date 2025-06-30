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


class CatalogueQuery(BaseModel):
    query_type:          str  # performers | studios
    query_string:        str|None = None
    use_sort_performers: bool = False
    
    filter_performer:   str|None = None
    filter_studio:      str|None = None
    filter_collection:  str|None = None
    filter_tag:         str|None = None

