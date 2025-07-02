
import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js';
import {generate_results} from '../../shared/util/search.js'

injectComponents();


const related_videos_load_amount = 24;
let related_videos_loaded = 0;


const load_related_videos = (video_hash, start_idx) => {
    makeApiRequestGET('/api/query/get/similar-videos', [video_hash, start_idx + 1, related_videos_load_amount], search_results => {
        generate_results(search_results);
    });
    return start_idx + related_videos_load_amount
};


makeApiRequestGET('/api/get/random-spotlight-video-hash', [], (initial_response) => {
    
    console.log(initial_response);
    makeApiRequestGET('/api/get/video-data', [initial_response.hash], (video_data) => {
        
        /* show date */
        let date = Date().split(' ').slice(0,4).join(' ');
        document.querySelector('.top-container h2').innerText += ' ' + date;
        
        /* load related videos */
        related_videos_loaded = load_related_videos(video_data.hash, related_videos_loaded);
        document.getElementById('expand-results-button').addEventListener('click', () => {
            related_videos_loaded = load_related_videos(video_data.hash, related_videos_loaded);
        });

    });
})



