package schemas

type VideoInteractions struct {
	Hash           string   `json:"hash"`
	LastViewed     *string  `json:"last_viewed,omitempty"`
	Viewtime       float64  `json:"viewtime"`
	IsFavourite    bool     `json:"is_favourite"`
	FavouritedDate *string  `json:"favourited_date,omitempty"`
	Views          []string `json:"views"`
	Likes          int      `json:"likes"`
	Rating         *string  `json:"rating,omitempty"`

	Markers      [][3]interface{} `json:"markers"`       // (video_time, color, tag)
	DatedMarkers [][2]interface{} `json:"dated_markers"` // (video_time, datetime)
	Comments     [][2]interface{} `json:"comments"`      // (comment, datetime)

}
