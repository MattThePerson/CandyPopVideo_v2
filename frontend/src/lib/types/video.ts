export interface VideoData {
    hash:             string;
    date_added:       string;
    date_downloaded:  string;
    path:             string;
    filename:         string;

    duration:         string;   // formatted duration string
    filesize_mb:      number;
    fps:              number;
    resolution:       number;
    bitrate:          number;
    duration_seconds: number;

    source_id:        string;

    collection:       string;
    parent_dir:       string;
    path_relative:    string;

    title:            string;
    scene_title:      string;
    scene_number:     number;
    movie_title:      string;
    movie_series:     string;

    studio:           string;
    line:             string;
    date_released:    string;
    description:      string;
    dvd_code:         string;

    actors:           string[];
    primary_actors:   string[];
    secondary_actors: string[];

    tags:              string[];
    tags_from_filename:string[];
    tags_from_path:    string[];
    tags_from_json:    string[];
    genres:            string[];

    views:    number;
    likes:    number;

    metadata: Record<string, unknown> | null;
}

export interface VideoInteractions {
    hash:            string;
    last_viewed:     string;
    viewtime:        number;
    is_favourite:    boolean;
    favourited_date: string;
    likes:           number;

    rating: string;   // "S+", "S", "A+", "A", "B+", "B", "C+", "C"

    markers:       [number, string, string][];  // [video_time, color, tag]
    dated_markers: [number, string][];          // [video_time, datetime]
    comments:      [string, string][];          // [comment, datetime]
}
