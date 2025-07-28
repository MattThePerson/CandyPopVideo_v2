package routes

import "github.com/labstack/echo/v4"

type Query struct {
	SearchString     *string  `json:"search_string"`
	Actor            *string  `json:"actor"`
	Studio           *string  `json:"studio"`
	Collection       *string  `json:"collection"`
	IncludeTerms     []string `json:"include_terms"`
	ExcludeTerms     []string `json:"exclude_terms"`
	DateAddedFrom    *string  `json:"date_added_from"`
	DateAddedTo      *string  `json:"date_added_to"`
	DateReleasedFrom *string  `json:"date_released_from"`
	DateReleasedTo   *string  `json:"date_released_to"`
	OnlyFavourites   bool     `json:"only_favourites"`
	SortBy           *string  `json:"sortby"`
	Limit            int      `json:"limit"`
	StartFrom        int      `json:"startfrom"`
}

type CatalogueQuery struct {
	QueryType        string  `json:"query_type"` // performers | studios
	QueryString      *string `json:"query_string"`
	UsePrimaryActors bool    `json:"use_primary_actors"`

	FilterActor      *string `json:"filter_actor"`
	FilterStudio     *string `json:"filter_studio"`
	FilterCollection *string `json:"filter_collection"`
	FilterTag        *string `json:"filter_tag"`
}

func IncludeQueryRoutes(e *echo.Group) {

	// get videodata
	e.POST("/search-videos", func(c echo.Context) error {
		var q Query
		err := c.Bind(&q)
		if err != nil {
			return c.String(400, "Invalid JSON")
		}
		// Handle request ...
		return c.JSON(200, map[string]interface{}{
			"search_results":        []int{1, 2, 3, 4},
			"videos_filtered_count": 69,
		})
	})

	// get catalogue
	e.POST("/get/catalogue", func(c echo.Context) error {
		var q CatalogueQuery
		err := c.Bind(&q)
		if err != nil {
			return c.String(400, "Invalid JSON")
		}
		// Handle request ...
		return c.String(501, "Not implemented")
	})

}
