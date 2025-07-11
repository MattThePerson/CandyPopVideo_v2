
import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js';
import { generate_results } from '../../shared/util/load.js';
import '../../shared/web_components/search_result_cards/default_card.js'

injectComponents();



const load_similar_videos = (results_container, video_hash, start_idx, load_amount) => {
    makeApiRequestGET('/api/query/get/similar-videos', [video_hash, start_idx + 1, load_amount], search_results => {
        generate_results(search_results, results_container);
    });
    return start_idx + load_amount;
};


/* API REQUEST */

makeApiRequestGET('/api/get/random-spotlight-video-hash', [], (initial_response) => {
    
    console.log(initial_response);
    initial_response.hash = '121a23562d15'; // 'b213a0d3edbe' // '00c1f7c43d27';

    makeApiRequestGET('/api/get/video-data', [initial_response.hash], (video_data) => {

        console.log(video_data);

        /* show date */
        let date = Date().split(' ').slice(0,4).join(' ');
        document.querySelector('.target-video-section h3').innerText += ' ' + date;
        
        /* add spotlight video */
        $('.target-video-container').html(/* html */`
            <search-result-card-default
                highlighted = true
                use_video_teasers = true
                width = "32rem"
                video_hash =        "${video_data.hash}"
                title =             "${video_data.title}"
                actors =            "${video_data.actors}"
                studio =            "${video_data.studio}"
                line =              "${video_data.line}"
                date_released =     "${video_data.date_released}"
                description =       "${video_data.description}"
                collection =        "${video_data.collection}"
                dvd_code =          "${video_data.dvd_code}"
                duration =          "${video_data.duration}"
                resolution =        "${video_data.resolution}"
                fps =               "${video_data.fps}"
                bitrate =           "${video_data.bitrate}"
                date_added =        "${video_data.date_added}"
                tags =              "${video_data.tags}"
                filename =          "${video_data.filename}"
            ></search-result-card-default>
        `);


        // poster = ""
        // teaser (small) = ""
        // teaser thumbs (spritesheet) = ""
        
        /* load related videos */

        const similar_videos_load_amount = 8 //24;
        let similar_videos_loaded = 0;
        
        const results_container = $('.similar-videos-section')
        similar_videos_loaded = load_similar_videos(results_container, video_data.hash, similar_videos_loaded, similar_videos_load_amount);
        document.getElementById('expand-results-button').addEventListener('click', () => {
            similar_videos_loaded = load_similar_videos(results_container, video_data.hash, similar_videos_loaded, similar_videos_load_amount);
        });

    });
})

