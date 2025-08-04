package schemas

type VideoInteractions struct {
	Hash           string  `json:"hash"`
	LastViewed     string  `json:"last_viewed"`
	Viewtime       float64 `json:"viewtime"`
	IsFavourite    bool    `json:"is_favourite"`
	FavouritedDate string  `json:"favourited_date"`
	// Views          []string `json:"views"`
	Likes int `json:"likes"`

	Rating      string `json:"rating"`       // S+, A, ...
	RatingScore int    `json:"rating_score"` // numerical

	Markers      [][3]any    `json:"markers"`       // (video_time, color, tag)
	DatedMarkers [][2]any    `json:"dated_markers"` // (video_time, datetime)
	Comments     [][2]string `json:"comments"`      // (comment, datetime)

}

/*
RATING_SCORE:
S+ -> 7   #  core memory
S  -> 6   #  outstanding
A+ -> 5   #
A  -> 4   #  good
B+ -> 3   #
B  -> 2   #
C+ -> 1   #  *some* reason to be in my collection
C  -> 0   #  no reason to be in my collection

*/
