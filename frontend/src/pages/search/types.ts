import type { VideoData } from "$lib/types/video";

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

export interface SearchResponse {
    search_results:         VideoData[],
    time_taken:             number,
    videos_filtered_count:  number,
    word_cloud:             unknown[][], // nothing yet, define as interface later when implementing word cloud
}
