package query

import (
	"log"
	"slices"
	"strings"
	"time"

	"cpv_backend/internal/schemas"
)

type ItemInfo struct {
	Name 			string
	VideoCount 		int
	NewestVideo 	string
	NewVideoCount 	int
}

type Catalogue struct {
	ActorInfo      []ItemInfo `json:"actor_info"`
	StudioInfo     []ItemInfo `json:"studio_info"`
	CollectionInfo []ItemInfo `json:"collection_info"`
	TagInfo        []ItemInfo `json:"tag_info"`
	TimeTakenMS    float64    `json:"time_taken_ms"`
}

// #region - PUB --------------------------------------------------------------------------------------------------------

// GetCatalogue gets info on videos grouped by different item types, (eg. actor)
func GetCatalogue(vids []schemas.VideoData, q schemas.CatalogueQuery) (Catalogue, error) {

	start := time.Now()
	var cat Catalogue

	// determine actor type
	getVideoActors := getVideoActors_All
	if q.UsePrimaryActors {
		getVideoActors = getVideoActors_Primary
	}

	/* FILTER */
	if q.FilterActor != "" {
		lw := strings.ToLower(q.FilterActor)
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return slices.Contains(getVideoActors(vd), lw)
		})
	}
	if q.FilterStudio != "" {
		lw := strings.ToLower(q.FilterStudio)
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return slices.Contains(getVideoStudios(vd), lw)
		})
	}
	if q.FilterCollection != "" {
		lw := strings.ToLower(q.FilterCollection)
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return slices.Contains(getVideoCollection(vd), lw)
		})
	}
	if q.FilterTag != "" {
		lw := strings.ToLower(q.FilterTag)
		vids = filterSliceFunc(vids, func(vd schemas.VideoData) bool {
			return slices.Contains(getVideoTags(vd), lw)
		})
	}
	
	
	/* GET ITEM INFOS */
	cat.ActorInfo = 	 getItemInfo(vids, getVideoActors)
	cat.StudioInfo = 	 getItemInfo(vids, getVideoStudios)
	cat.CollectionInfo = getItemInfo(vids, getVideoCollection)
	cat.TagInfo = 		 getItemInfo(vids, getVideoTags)

	
	/* TF-IDF */
	if q.QueryString != "" {
		// ...
	}
	
	cat.TimeTakenMS = float64(time.Since(start).Microseconds())/1000
	return cat, nil
	
}


// #region - PRIV ------------------------------------------------------------------------------------------------------


// 
func getItemInfo(vids []schemas.VideoData, item_extractor_func func(schemas.VideoData)[]string) []ItemInfo {

	item_counts := map[string]int{}
	newest_video := map[string]string{}
	// oldest_video := map[string]string{}
	new_videos := map[string]int{}

	for _, vd := range vids {
		for _, item := range item_extractor_func(vd) {
			item_counts[item] = item_counts[item] + 1
			// update item newest video
			newest_date_added, ok := newest_video[item]
			if !ok {
				newest_date_added = "1970-01-01T00:01"
			}
			if vd.DateAdded > newest_date_added {
				newest_video[item] = vd.DateAdded
			}
			// update new videos
			if secondsFromNow(vd.DateAdded) < (60*60*24*7) {
				new_videos[item] = new_videos[item] + 1
			}
		}
	}

	var item_infos []ItemInfo
	for k := range item_counts {
		info := ItemInfo{
			Name: 			k,
			VideoCount: 	item_counts[k],
			NewestVideo: 	newest_video[k],
			NewVideoCount: 	new_videos[k],
		}
		item_infos = append(item_infos, info)
	}
	return item_infos
}

/* ITEM GETTERS */

func getVideoActors_All(vd schemas.VideoData) []string {
	slic := []string{}
	for _, a := range vd.Actors {
		slic = append(slic, standardizeString(a))
	}
	return slic
}

func getVideoActors_Primary(vd schemas.VideoData) []string {
	slic := []string{}
	for _, a := range vd.PrimaryActors {
		slic = append(slic, standardizeString(a))
	}
	return slic
}

func getVideoStudios(vd schemas.VideoData) []string {
	var slic []string
	if vd.Studio != "" {
		slic = append(slic, standardizeString(vd.Studio))
	}
	if vd.Line != "" {
		slic = append(slic, standardizeString(vd.Line))
	}
	return slic
}

func getVideoCollection(vd schemas.VideoData) []string {
	return []string{standardizeString(vd.Collection)}
}

func getVideoTags(vd schemas.VideoData) []string {
	slic := []string{}
	for _, a := range vd.Tags {
		slic = append(slic, standardizeString(a))
	}
	return slic
}

// #region - HELPERS ---------------------------------------------------------------------------------------------------


func secondsFromNow(date string) float64 {
    const layout = "2006-01-02 15:04"
    t, err := time.Parse(layout, date)
    if err != nil {
        log.Println("error parsing date: "+err.Error())
        return 0
    }
    duration := time.Since(t)
    return duration.Seconds()
}
