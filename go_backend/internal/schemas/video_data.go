package schemas

type VideoData struct {

	//
	Hash      string `json:"hash"`
	DateAdded string `json:"date_added"`
	Path      string `json:"path"`
	Filename  string `json:"filename"`

	// video attributes
	Duration        string  `json:"duration"`
	FilesizeMB      float64 `json:"filesize_mb"`
	FPS             float64 `json:"fps"`
	Resolution      int     `json:"resolution"`
	Bitrate         int     `json:"bitrate"`
	DurationSeconds float64 `json:"duration_seconds"`

	SourceID *string `json:"source_id,omitempty"`

	// collection
	Collection   *string `json:"collection,omitempty"`
	ParentDir    *string `json:"parent_dir,omitempty"`
	PathRelative *string `json:"path_relative,omitempty"`

	// scene attributes
	Title       *string `json:"title,omitempty"`
	SceneTitle  *string `json:"scene_title,omitempty"`
	SceneNumber *int    `json:"scene_number,omitempty"`
	MovieTitle  *string `json:"movie_title,omitempty"`
	MovieSeries *string `json:"movie_series,omitempty"`

	Studio       *string `json:"studio,omitempty"`
	Line         *string `json:"line,omitempty"`
	DateReleased *string `json:"date_released,omitempty"`
	Description  *string `json:"description,omitempty"`
	DVDCode      *string `json:"dvd_code,omitempty"`
	// D18Url       		*string `json:"d18_url"`
	// DateReleasedD18     *string `json:"date_released_d18"`

	Actors          []string `json:"actors"`
	PrimaryActors   []string `json:"primary_actors"`
	SecondaryActors []string `json:"secondary_actors"`

	// meta
	Tags             []string `json:"tags"`
	TagsFromFilename []string `json:"tags_from_filename"`
	TagsFromPath     []string `json:"tags_from_path"`
	TagsFromJSON     []string `json:"tags_from_json"`
	Genres           []string `json:"genres"`
	// TagsFromD18	     []string `json:"tags_from_d18"`

	Metadata map[string]any `json:"metadata"`

	IsLinked bool `json:"is_linked"`
}
