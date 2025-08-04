package query

import (
	"cmp"
	"encoding/json"
	"fmt"
	"reflect"
	"slices"
	"strconv"
	"strings"
	"time"

	"cpv_backend/internal/schemas"
)

type FilterAndSortResult struct {
	SearchResults []schemas.VideoData 	`json:"search_results"`
	FilteredCount int 					`json:"videos_filtered_count"`
	WordCloud     [][]any               `json:"word_cloud"`
	TimeTakenMS   float64				`json:"time_taken"`
}

func FilterAndSortVideos(vids []schemas.VideoData, q schemas.SearchQuery, i map[string]schemas.VideoInteractions) (FilterAndSortResult, error) {
	
	start := time.Now()
	var result FilterAndSortResult
	var err error

	// default limit and startfrom
	if q.Limit <= 0 {
		q.Limit = 512
	}
	if q.StartFrom <= 0 {
		q.StartFrom = 0
	}

	// filters
	vids = filterVideosBySearchQuery(vids, q, i)

	// sort
	if q.SortBy == "" {
		slices.SortFunc(vids, func(a, b schemas.VideoData) int {
			return cmp.Compare(b.DateAdded, a.DateAdded)
		})
	} else {
		vids, err = sortVideos(vids, q.SortBy, i)
		if err != nil {
			return result, err
		}
	}
	
	// get word cloud
	result.WordCloud = nil

	result.FilteredCount = len(vids)
	result.SearchResults = getSubSliceSafe(vids, q.StartFrom, q.StartFrom+q.Limit)

	result.TimeTakenMS = float64(time.Since(start).Microseconds())/1000
	return result, nil

}


// #region - METHODS ---------------------------------------------------------------------------------------------------


// 
func filterVideosBySearchQuery(vids []schemas.VideoData, q schemas.SearchQuery, i map[string]schemas.VideoInteractions) []schemas.VideoData {

	// filter only favourites
	if q.OnlyFavourites == "true" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			inter, ok := i[vd.Hash]
			return (ok && inter.IsFavourite)
		})
	}

	// actor
	if q.Actor != "" {
		q_actors := strings.Split(q.Actor, ",")
		for _, q_actor := range q_actors {
			q_actor = strings.TrimSpace(q_actor)
			vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
				for _, vid_actor := range vd.Actors {
					if strings.EqualFold(vid_actor, q_actor) {
						return true;
					}
				}
				return false
			})
		}
	}

	// studio
	if q.Studio != "" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return 	(vd.Studio != "" && strings.EqualFold(vd.Studio, q.Studio)) ||
					(vd.Line != ""   && strings.EqualFold(vd.Line, q.Studio))
		})
	}

	// collection
	if q.Collection != "" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return strings.EqualFold(q.Collection, vd.Collection)
		})
	}

	// date added from
	if q.DateAddedFrom != "" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return vd.DateAdded >= q.DateAddedFrom
		})
	}

	// date added to
	if q.DateAddedTo != "" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return vd.DateAdded < q.DateAddedTo
		})
	}

	// date released from
	if q.DateReleasedFrom != "" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return vd.DateReleased != "" && vd.DateReleased >= q.DateReleasedFrom
		})
	}

	// date released to
	if q.DateReleasedTo != "" {
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return vd.DateReleased != "" && vd.DateReleased < q.DateReleasedTo
		})
	}

	// include terms
	for _, t := range q.IncludeTerms {
		t = strings.ToLower(t)
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return strings.Contains(strings.ToLower(vd.Path), t)
		})
	}

	// exclude terms
	for _, t := range q.ExcludeTerms {
		t = strings.ToLower(t)
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return !strings.Contains(strings.ToLower(vd.Path), t)
		})
	}

	return vids
}


// 
func sortVideos(vids []schemas.VideoData, sortby string, i map[string]schemas.VideoInteractions) ([]schemas.VideoData, error) {

	var err error
	
	// OPTION 1: sort random
	if strings.Contains(sortby, "random") {
		vids, err = handleSortVideosRandom(vids, sortby)
		if err != nil {
			return vids, err
		}
		return vids, nil
	}

	// extract sortby params
	var sort_reverse = strings.Contains(sortby, "desc")
	var sortby_attr = strings.ReplaceAll(sortby, "-", "_")
	for _, opt := range []string{"_asc", "_desc"} {
		sortby_attr = strings.ReplaceAll(sortby_attr, opt, "")
	}
	fmt.Printf("SORTBY_ATTR: %s\nSORT_REVERSE: %t\n", sortby_attr, sort_reverse)

	// OPTION 2: sort by interactions
	SORTBY_OPTIONS := []string{"viewtime", "last_viewed", "favourited_date", "popularity"}
	if slices.Contains(SORTBY_OPTIONS, sortby_attr) {
		vids, err = handleSortByInteractions(vids, sortby_attr, sort_reverse, i)
		if err != nil {
			return vids, err
		}
		return vids, nil
	}

	// OPTION 3: sort by video data
	vids, err = handleSortByVideoData(vids, sortby_attr, sort_reverse)
	if err != nil {
		return vids, err
	}
	return vids, nil

}


//handleSortByVideoData
func handleSortByVideoData(vids []schemas.VideoData, attr string, reverse bool) ([]schemas.VideoData, error) {

	// convert to maps
	vid_maps, err := structsToMaps(vids)
	if err != nil {
		return vids, nil
	}
	
	// sort by attribute
	slices.SortFunc(vid_maps, func(a, b map[string]any) int {
		va, vb := a[attr], b[attr]
		if reflect.TypeOf(va) != reflect.TypeOf(vb) || va == nil || vb == nil {
			return 0
		}

		if reverse {
			vb, va = va, vb
		}

		switch v := va.(type) {
			case string:	return cmp.Compare(v, vb.(string))
			case int:		return cmp.Compare(v, vb.(int))
			case float64:	return cmp.Compare(v, vb.(float64))
		}
		return 0
	})

	// convert to structs
	vids, err = mapsToStructs[schemas.VideoData](vid_maps)
	if err != nil {
		return vids, err
	}
	return vids, nil
}

//handleSortByInteractions
func handleSortByInteractions(vids []schemas.VideoData, attr string, reverse bool, i map[string]schemas.VideoInteractions) ([]schemas.VideoData, error) {
	// filter videos if no interactions
	filtered := []schemas.VideoData{}
	for _, vd := range vids {
		if _, ok := i[vd.Hash]; ok {
			filtered = append(filtered, vd)
		}
	}

	// add popularity
	var popularity = map[string]float64{}
	if attr == "popularity" {
		for _, vd := range filtered {
			popularity[vd.Hash] = getInteractionPopularity(i[vd.Hash])
		}
	}

	// sort by interaction metric
	slices.SortFunc(filtered, func(a, b schemas.VideoData) int {
		if reverse {
			a, b = b, a
		}
		
		i1, i2 := i[a.Hash], i[b.Hash]

		switch attr {
		case "viewtime":
			return int(i1.Viewtime - i2.Viewtime)
		case "last_viewed":
			return cmp.Compare(i1.LastViewed, i2.LastViewed)
		case "favourited_date":
			return cmp.Compare(i1.FavouritedDate, i2.FavouritedDate)
		case "popularity":
			return int(popularity[a.Hash] - popularity[b.Hash])
		}
		
		return 0
	})
	
	return filtered, nil
}


// getInteractionPopularity
func getInteractionPopularity(i schemas.VideoInteractions) float64 {
	var points float64
	points += i.Viewtime/60 // 1 min/point
	points += float64( i.Likes*2 ) // 2 mins
	if i.IsFavourite { points += 2 } // 2 mins (TEMPORARILY LOWER!)
	points += float64( len(i.Comments) * 3 ) // 3 mins
	points += float64( len(i.Markers) * 1 ) // 1 mins
	points += float64( len(i.DatedMarkers) * 5 ) // 5 mins
	points += float64( i.RatingScore * 2 ) // max -> 14 mins
	return points
}


// sort deterministic
func handleSortVideosRandom(vids []schemas.VideoData, sortby string) ([]schemas.VideoData, error) {
	slices.SortFunc(vids, func(a, b schemas.VideoData) int {
		return cmp.Compare(b.DateAdded, a.DateAdded)
	})
	// extract seed
	parts := strings.Split(sortby, "-")
	lastStr := parts[len(parts)-1]
	seed, err := strconv.Atoi(lastStr)
	if err != nil {
		return vids, err
	}
	// shuffle random
	vids = seededShuffle_Perm(vids, int64(seed))
	
	return vids, nil
}


func structsToMaps[S any](input []S) ([]map[string]any, error) {

	output := make([]map[string]any, len(input))

	var err error
	var data []byte

	for i, a := range input {
		// marshal to json
		data, err = json.Marshal(&a)
		if err != nil {
			return output, err
		}
		// unmarshal to map
		var b map[string]any
		err = json.Unmarshal(data, &b)
		if err != nil {
			return output, err
		}
		// append
		output[i] = b
	}
	
	return output, nil
}


func mapsToStructs[S any](input []map[string]any) ([]S, error) {

	output := make([]S, len(input))

	var err error
	var data []byte

	for i, a := range input {
		// marshal to json
		data, err = json.Marshal(&a)
		if err != nil {
			return output, err
		}
		// unmarshal to map
		var b S
		err = json.Unmarshal(data, &b)
		if err != nil {
			return output, err
		}
		// append
		output[i] = b
	}
	
	
	return output, nil
}