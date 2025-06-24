

class VideoHandler {

    constructor(videoSet) {
        this.hashes = Object.keys(videoSet);
        this.videos = this.hashes.map(hash => {
            let videoItem = videoSet[hash];
            videoItem['hash'] = hash;
            return videoItem;
        });
        this.filenames = this.videos.map(video => {
            return video["filename"];
        });
        this.studios = Array.from(new Set(
            this.videos.map(video => {return video["studio"] })
        ));
        this.actors = Array.from(new Set(
            this.videos.flatMap(video => { return video["actors"] })
        ));
        this.collections = Array.from(new Set(
            this.videos.map(video => {return video["collection"]})
        ));
    }

    getVideos(start_i, length) {
        return this.videos.slice(start_i, start_i+length);
    }
    
    sortVideos(param, reverse) {
        //
    }

    filterVideos() {
        //
    }

    // calculates relevance score for each video based on query, sorts video by relevance
    // and removes
    applySearchQuery(query, threshold) {
        //
    }
}