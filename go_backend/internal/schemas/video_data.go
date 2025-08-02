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

	SourceID string `json:"source_id"`

	// collection
	Collection   string `json:"collection"`
	ParentDir    string `json:"parent_dir"`
	PathRelative string `json:"path_relative"`

	// scene attributes
	Title       string `json:"title"`
	SceneTitle  string `json:"scene_title"`
	SceneNumber *int   `json:"scene_number"`
	MovieTitle  string `json:"movie_title"`
	MovieSeries string `json:"movie_series"`

	Studio       string `json:"studio"`
	Line         string `json:"line"`
	DateReleased string `json:"date_released"`
	Description  string `json:"description"`
	DVDCode      string `json:"dvd_code"`
	// D18Url       		string `json:"d18_url"`
	// DateReleasedD18     string `json:"date_released_d18"`

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
