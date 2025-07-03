
import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js';
import '../../shared/web_components/search_result_cards/default_card.js'

injectComponents();


const related_videos_load_amount = 4 //24;
let related_videos_loaded = 0;


const load_related_videos = (results_container, video_hash, start_idx) => {
    makeApiRequestGET('/api/query/get/similar-videos', [video_hash, start_idx + 1, related_videos_load_amount], search_results => {
        generate_results_new(results_container, search_results);
    });
    return start_idx + related_videos_load_amount
};


/* API REQUEST */

makeApiRequestGET('/api/get/random-spotlight-video-hash', [], (initial_response) => {
    
    console.log(initial_response);
    initial_response.hash = '75d4f90d52c9';

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

        const results_container = $('.related-videos-section')
        related_videos_loaded = load_related_videos(results_container, video_data.hash, related_videos_loaded);
        document.getElementById('expand-results-button').addEventListener('click', () => {
            related_videos_loaded = load_related_videos(results_container, video_data.hash, related_videos_loaded);
        });

    });
})


function generate_results_new(resultsContainer, results) {
    
    resultsContainer.css('visibility', 'visible');
    
    let html_content = '';
    results.search_results.forEach( (result) => {
        html_content += /* html */`
            <search-result-card-default
                scene_title =       "${result.scene_title}"
                performers =        "${result.performers}"
                studio =            "${result.studio}"
                line =              "${result.line}"
                date_released =     "${result.date_released}"
                year =              "${result.year}"
                scene_description = "${result.scene_description}"
                collection =        "${result.collection}"
                jav_code =          "${result.jav_code}"
                duration =          "${result.duration}"
                resolution =        "${result.resolution}"
                fps =               "${result.fps}"
                bitrate =           "${result.bitrate}"
                hash =              "${result.hash}"
                date_added =        "${result.date_added}"
                tags =              "${result.tags}"
                filename =          "${result.filename}"
            ></search-result-card-default>
        `
    });
    resultsContainer.find('.video-cards-styler').append(html_content)
    

    // Configure page nav
    if (args && args.generate_nav) {
        const amount_of_results = results.videos_filtered_count;
        const number_of_pages = Math.max(1, Math.floor((amount_of_results-1) / query.limit) + 1);
        document.querySelector('#search-page-info .page-number').innerText += ' of ' + number_of_pages + ' (' + amount_of_results + ' search results, took ' + results.time_taken + ' seconds)';
        const current_page = Math.floor(query.startfrom / query.limit);
        const max_buttons = 11;
        
        const pageNav = document.getElementById('page-nav');
        const pageNavButtonsContainer = pageNav.querySelector('.page-nav-buttons-container');
        const prevPageButton = pageNav.querySelector('.prev-page');
        const nextPageButton = pageNav.querySelector('.next-page');

        let pages = getPageNavNumbers(current_page+1, number_of_pages, max_buttons);

        for (let i of pages) {
            let button = document.createElement('button');
            if (i == -1) {
                button.classList.add('filler-button');
                button.innerText = '...';
            } else {
                button.id = 'page-' + i;
                button.innerText = i;
                if (i == current_page+1) {
                    button.classList.add('selected');
                } else {
                    button.addEventListener('click', event => {
                        switch_to_page(i);
                    });
                }
            }
            pageNavButtonsContainer.appendChild( button );
        }

        if (current_page > 0) {
            prevPageButton.addEventListener('click', arg => {
                console.log("clicked prev page button");
                switch_to_page(current_page);
            });
        } else {
            prevPageButton.classList.add('inactive');
        }
        if (current_page < number_of_pages-1) {
            nextPageButton.addEventListener('click', arg => {
                console.log("clicked next page button");
                switch_to_page(current_page+2);
            });
        } else {
            nextPageButton.classList.add('inactive');
        }

        const pageNumberInput = document.querySelector('.page-number-input');
        pageNumberInput.addEventListener('keydown', event => {
            console.log('Keydown in input');
            if (event.key === 'Enter' && pageNumberInput.value != '') {
                let n = parseInt(pageNumberInput.value);
                n = Math.max(0, n);
                n = Math.min(number_of_pages, n);
                switch_to_page(n);
            }
        });
    }
    
}