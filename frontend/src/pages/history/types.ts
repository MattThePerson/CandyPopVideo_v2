export interface ViewingRow {
    id:           number;
    video_hash:   string;
    datetime:     string;
    time_start:   number;
    duration_sec: number;
}

export interface ViewingSession {
    video_hash: string;
    start_dt:   Date;
    total_sec:  number;
    segments:   ViewingRow[];
}
