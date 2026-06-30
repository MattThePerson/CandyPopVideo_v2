package schemas

import (
    "slices"
    "math"
)

type VideoInteractions struct {
    Hash           string  `json:"hash"`
    LastViewed     string  `json:"last_viewed"`
    Viewtime       float64 `json:"viewtime"`
    IsFavourite    bool    `json:"is_favourite"`
    FavouritedDate string  `json:"favourited_date"`
    Likes int `json:"likes"`

    Rating string `json:"rating"`

    Markers      [][3]any    `json:"markers"`       // (video_time, color, tag)
    DatedMarkers [][2]any    `json:"dated_markers"` // (video_time, datetime)
    Comments     [][2]string `json:"comments"`      // (comment, datetime)
}

// getInteractionPopularity
func (i VideoInteractions) GetUserPopularity() float64 {
    var points float64
    points += getLogAdjustedPoints( i.Viewtime/60, 7.0, 0.129 )
    points += getLogAdjustedPoints( float64(len(i.Markers)), 7.0, 0.129 )
    points += float64( i.Likes*2 )
    if i.IsFavourite { points += 7 }
    points += float64( len(i.Comments) * 3 )
    points += float64( len(i.DatedMarkers) * 5 )
    points += float64( ratingToInt(i.Rating) )
    return points
}

// getLogAdjustedPoints returns the value of the function a * ln(b * x + 1)
func getLogAdjustedPoints(x float64, a float64, b float64) float64 {
    return a * math.Log(b * x + 1)
}

// VideoInteractionsResponse is the API response shape — wraps VideoInteractions
// and injects computed fields that must not be persisted to the DB.
type VideoInteractionsResponse struct {
    VideoInteractions
    PopularityScore float64 `json:"popularity_score"`
}

// ToResponse computes derived fields and returns the API-safe wrapper.
func (i VideoInteractions) ToResponse() VideoInteractionsResponse {
    return VideoInteractionsResponse{
        VideoInteractions: i,
        PopularityScore:   i.GetUserPopularity(),
    }
}

var ratingStrings = []string{"C", "C+", "B", "B+", "A", "A+", "S", "S+"}

// ratingToInt converts the string rating into integer such that
// C=0, C+=0, B=2, B+=3, A=4, A+=5, S=6, S+=7
func ratingToInt(r string) int {
    idx := slices.Index(ratingStrings, r)
    if idx < 0 {
        return 0
    }
    return idx
}
