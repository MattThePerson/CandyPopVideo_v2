export interface SearchQuery {
    search_string:      string;
    actor:              string;
    studio:             string;
    collection:         string;
    include_terms:      string[];
    exclude_terms:      string[];
    tags:               string[];
    date_added_from:    string;
    date_added_to:      string;
    date_released_from: string;
    date_released_to:   string;
    only_favourites:    string;
    sortby:             string;
    limit:              number;
    startfrom:          number;
}

export interface CatalogueQuery {
    query_type:         string;   // "actors" | "studios"
    query_string:       string;
    use_primary_actors: boolean;
    filter_actor:       string;
    filter_studio:      string;
    filter_collection:  string;
    filter_tag:         string;
}
