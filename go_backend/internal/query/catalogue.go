package query

import "cpv_backend/internal/schemas"

type Catalogue struct {
	ActorInfo      [][]any `json:"actor_info"`
	StudioInfo     [][]any `json:"studio_info"`
	CollectionInfo [][]any `json:"collection_info"`
	TagInfo        [][]any `json:"tag_info"`

	TimeTakenMS    float64 `json:"time_taken_ms"`
}

func GetCatalogue(videos_list []schemas.VideoData, query schemas.CatalogueQuery) (Catalogue, error) {

	var cat Catalogue

	// use sort performers
	// ...

	// filter
	// ...

	// get items
	cat.ActorInfo = [][]any{}
	cat.StudioInfo = [][]any{}
	cat.CollectionInfo = [][]any{}
	cat.TagInfo = [][]any{}

	// sort
	// ...

	return cat, nil
	
}
