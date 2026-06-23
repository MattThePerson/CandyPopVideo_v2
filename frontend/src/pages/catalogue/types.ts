export type CatalogueTab = 'actors' | 'studios' | 'collections' | 'tags';
export type SortMode     = 'alphabetic' | 'count' | 'newest-video';

export interface CatalogueQuery {
    query_type:         string;
    query_string:       string;
    use_primary_actors: boolean;
    filter_actor:       string;
    filter_studio:      string;
    filter_collection:  string;
    filter_tag:         string;
}

export interface ItemInfo {
    name:            string;
    video_count:     number;
    newest_video:    string;
    new_video_count: number;
}

export interface Catalogue {
    actor_info:      ItemInfo[];
    studio_info:     ItemInfo[];
    collection_info: ItemInfo[];
    tag_info:        ItemInfo[];
    time_taken_ms:   number;
}
