package schemas

type VideoData struct {

    //
    Hash           string `json:"hash"`
    DateAdded      string `json:"date_added"`      // when first scanned into DB; set once
    DateDownloaded string `json:"date_downloaded"` // file ModTime at first scan; set once
    Path           string `json:"path"`
    Filename       string `json:"filename"`

    // video attributes
    Duration        string  `json:"duration"`
    DurationSeconds float64 `json:"duration_seconds"`
    FilesizeMB      float64 `json:"filesize_mb"`
    FPS             float64 `json:"fps"`
    Height          int     `json:"height"`
    Width           int     `json:"width"`
    Resolution      string  `json:"resolution"` // "1920x1080"
    AspectRatio     string  `json:"aspect_ratio"`
    Bitrate         int     `json:"bitrate"`
    IsVFR           bool    `json:"is_vfr"`
    VideoCodec      string  `json:"video_codec"`
    AudioCodec      string  `json:"audio_codec"`
    PixFmt          string  `json:"pix_fmt"`
    ColorTransfer   string  `json:"color_transfer"`

    SourceID string `json:"source_id"`

    // collection
    Collection   string `json:"collection"`
    ParentDir    string `json:"parent_dir"`
    PathRelative string `json:"path_relative"`

    // scene attributes
    Title       string `json:"title"`
    SceneTitle  string `json:"scene_title"`
    SceneNumber int    `json:"scene_number"`
    MovieTitle  string `json:"movie_title"`
    MovieSeries string `json:"movie_series"`

    Studio       string `json:"studio"`
    Line         string `json:"line"`
    DateReleased string `json:"date_released"`
    Description  string `json:"description"`
    DVDCode      string `json:"dvd_code"`

    Actors          []string `json:"actors"`
    PrimaryActors   []string `json:"primary_actors"`
    SecondaryActors []string `json:"secondary_actors"`

    // meta
    Tags             []string `json:"tags"`
    TagsFromFilename []string `json:"tags_from_filename"`
    TagsFromPath     []string `json:"tags_from_path"`
    TagsFromJSON     []string `json:"tags_from_json"`
    Genres           []string `json:"genres"`

    // crawled interactions
    Views int `json:"views"`
    Likes int `json:"likes"`

    Metadata map[string]any `json:"metadata"`
}
