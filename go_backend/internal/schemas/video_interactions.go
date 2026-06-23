package schemas

type VideoInteractions struct {
	Hash           string  `json:"hash"`
	LastViewed     string  `json:"last_viewed"`
	Viewtime       float64 `json:"viewtime"`
	IsFavourite    bool    `json:"is_favourite"`
	FavouritedDate string  `json:"favourited_date"`
	// Views          []string `json:"views"`
	Likes int `json:"likes"`

	Rating string `json:"rating"` // S+, A, ...

	Markers      [][3]any    `json:"markers"`       // (video_time, color, tag)
	DatedMarkers [][2]any    `json:"dated_markers"` // (video_time, datetime)
	Comments     [][2]string `json:"comments"`      // (comment, datetime)

}

