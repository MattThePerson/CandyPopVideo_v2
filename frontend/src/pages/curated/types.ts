export interface CuratedQuery {
    search_string?:   string;
    actor?:           string;
    studio?:          string;
    collection?:      string;
    tags?:            string[];
    include_terms?:   string[];
    exclude_terms?:   string[];
    only_favourites?: string;
    sortby?:          string;
}

export interface CuratedCollectionMeta {
    name:        string;
    description: string;
    query:       CuratedQuery;
}
