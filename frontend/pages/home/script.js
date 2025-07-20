// @ts-ignore
const $ = window.$;

import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js';
import { render_video_cards } from '../../shared/util/load.js';

injectComponents();



/* API REQUEST */

makeApiRequestGET('/api/get/random-spotlight-video-hash', [], (initial_response) => {
    
    console.log(initial_response);
    // initial_response.hash = '121a23562d15'; // 'b213a0d3edbe' // '00c1f7c43d27';

    makeApiRequestGET('/api/get/video-data', [initial_response.hash], async (video_data) => {

        console.log(video_data);

        /* show date */
        let date = Date().split(' ').slice(0,4).join(' ');
        // document.querySelector('.target-video-section h3').innerText += ' ' + date;
        $('.target-video-section h3').text(function(i, t) {
            return t + ' ' + date;
        });
        
        /* add spotlight video */
        $('.target-video-container').html(/* html */`
            <search-result-card-default
                highlighted = true
                use_video_teasers = true
                width = "38rem"
                video_hash =        "${video_data.hash}"
                video_title =       "${video_data.title}"
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

        const card_type = "search-result-card-default"; // TODO: Replace with local storage

        const video_load_amount = 8 //24;

        const query_amount = 512
        const result = await $.get(`/api/query/get/similar-videos/${initial_response.hash}/0/${query_amount}`);
        let similar_videos = result.search_results;
        
        const results_container = $('.similar-videos-section').get(0);

        const expand_results_func = await render_video_cards(
            similar_videos,
            results_container,
            video_load_amount,
            1,
        )
        $(results_container).find('#expand-results-button').on('click', expand_results_func);

    });
})

