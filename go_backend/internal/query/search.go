package query

import (
	"cmp"
	"slices"
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

	// default limit and startfrom
	if q.Limit <= 0 {
		q.Limit = 12 // default
	}
	if q.StartFrom <= 0 {
		q.StartFrom = 0
	}

	// filters
	vids = filterVideosBySearchQuery(vids, q, i)

	// sort
	if q.SortBy != "" {
		vids = sortVideos(vids, q.SortBy, i)

	} else {
		slices.SortFunc(vids, func(a, b schemas.VideoData) int {
			return cmp.Compare(b.DateAdded, a.DateAdded)
		})

	}
	
	// get word cloud
	result.WordCloud = nil

	result.FilteredCount = len(vids)
	result.SearchResults = sliceSliceSafe(vids, q.StartFrom, q.StartFrom+q.Limit)

	result.TimeTakenMS = float64(time.Since(start).Microseconds())/1000
	return result, nil

}


// #region - METHODS ---------------------------------------------------------------------------------------------------


// 
func filterVideosBySearchQuery(vids []schemas.VideoData, q schemas.SearchQuery, i map[string]schemas.VideoInteractions) []schemas.VideoData {

	// filter only favourites
	// ...

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
func sortVideos(vids []schemas.VideoData, sortby string, i map[string]schemas.VideoInteractions) []schemas.VideoData {

	if strings.Contains(sortby, "random") {
		// ...

	} else {
		sort_reverse := strings.Contains(sortby, "desc")
		attr := strings.ReplaceAll(sortby, "-", "_")
		for _, opt := range []string{"_asc", "_desc"} {
			attr = strings.ReplaceAll(attr, opt, "")
		}
		slices.SortFunc(vids, func(a, b schemas.VideoData) int {
			if sort_reverse {
				return a.Bitrate - b.Bitrate
			}
			return b.Bitrate - a.Bitrate
		})

		if false {
			// sort by interactions
			// ...
		} else {

		}
		
	}

	return vids
}


