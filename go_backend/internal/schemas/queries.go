package schemas

type SearchQuery struct {
	SearchString     string   `json:"search_string"`
	Actor            string   `json:"actor"`
	Studio           string   `json:"studio"`
	Collection       string   `json:"collection"`
	IncludeTerms     []string `json:"include_terms"`
	ExcludeTerms     []string `json:"exclude_terms"`
	DateAddedFrom    string   `json:"date_added_from"`
	DateAddedTo      string   `json:"date_added_to"`
	DateReleasedFrom string   `json:"date_released_from"`
	DateReleasedTo   string   `json:"date_released_to"`
	OnlyFavourites   string   `json:"only_favourites"`
	SortBy           string   `json:"sortby"`
	Limit            int      `json:"limit"`
	StartFrom        int      `json:"startfrom"`
}

type CatalogueQuery struct {
	QueryType        string `json:"query_type"` // actors | studios
	QueryString      string `json:"query_string"`
	UsePrimaryActors bool   `json:"use_primary_actors"`

	FilterActor      string `json:"filter_actor"`
	FilterStudio     string `json:"filter_studio"`
	FilterCollection string `json:"filter_collection"`
	FilterTag        string `json:"filter_tag"`
}
