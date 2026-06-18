export interface CatalogueQuery {
    query_type:         string;   // "actors" | "studios"
    query_string:       string;
    use_primary_actors: boolean;
    filter_actor:       string;
    filter_studio:      string;
    filter_collection:  string;
    filter_tag:         string;
}
