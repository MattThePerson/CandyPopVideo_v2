
import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js';
import { generate_results } from '../../shared/util/load.js';
import '../../shared/web_components/search_result_cards/default_card.js'

injectComponents();


const related_videos_load_amount = 4 //24;
let related_videos_loaded = 0;

const load_related_videos = (results_container, video_hash, start_idx) => {
    makeApiRequestGET('/api/query/get/similar-videos', [video_hash, start_idx + 1, related_videos_load_amount], search_results => {
        generate_results(search_results, results_container);
    });
    return start_idx + related_videos_load_amount
};


/* API REQUEST */

makeApiRequestGET('/api/get/random-spotlight-video-hash', [], (initial_response) => {
    
    console.log(initial_response);
    initial_response.hash = '55c83646f03a';

    makeApiRequestGET('/api/get/video-data', [initial_response.hash], (video_data) => {

        console.log(video_data);

        /* show date */
        let date = Date().split(' ').slice(0,4).join(' ');
        document.querySelector('.target-video-section h3').innerText += ' ' + date;
        
        /* add spotlight video */
        $('.target-video-container').html(/* html */`
            <search-result-card-default
                highlighted = true
                width = "32rem"
                scene_title =       "${video_data.scene_title}"
                performers =        "${video_data.performers}"
                studio =            "${video_data.studio}"
                line =              "${video_data.line}"
                date_released =     "${video_data.date_released}"
                scene_description = "${video_data.scene_description}"
                collection =        "${video_data.collection}"
                jav_code =          "${video_data.jav_code}"
                duration =          "${video_data.duration}"
                resolution =        "${video_data.resolution}"
                fps =               "${video_data.fps}"
                bitrate =           "${video_data.bitrate}"
                hash =              "${video_data.hash}"
                date_added =        "${video_data.date_added}"
                tags =              "${video_data.tags}"
                filename =          "${video_data.filename}"
            ></search-result-card-default>
        `);


        // poster = ""
        // teaser (small) = ""
        // teaser thumbs (spritesheet) = ""
        
        /* load related videos */

        const results_container = $('.similar-videos-section')
        related_videos_loaded = load_related_videos(results_container, video_data.hash, related_videos_loaded);
        document.getElementById('expand-results-button').addEventListener('click', () => {
            related_videos_loaded = load_related_videos(results_container, video_data.hash, related_videos_loaded);
        });

    });
})

