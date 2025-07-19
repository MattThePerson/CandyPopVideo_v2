import { render_video_cards } from "../../shared/util/load.js";
import { makeApiRequestPOST_JSON } from "../../shared/util/request.js"


const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

//region - PUBLIC ------------------------------------------------------------------------------------------------------

/**
 * 
 * @param {Object} vd 
 * @param {HTMLElement} related_sec 
 * @param {HTMLElement} similar_sec 
 * @param {string} video_hash
 */
export async function load_recommended_videos(vd, related_sec, similar_sec, video_hash) {
    

    /* STEP 1: Get related videos (that will be removed from similar videos) */
    let start = Date.now();
    const related_videos_dict = {};

    if (vd.movie_title) {
        const result = await $.get('/api/get/movie/'+vd.movie_title);
        if (Array.isArray(result) && result.length > 0) {
            related_videos_dict['movie'] = result;
            related_videos_dict['movie'] = {
                'videos': result,
                'title': `movie title: "${vd.movie_title}"  (${result.length} videos)`,
            };
        }
    }

    if (vd.movie_series) {
        const result = await $.get('/api/get/movie-series/'+vd.movie_series);
        if (Array.isArray(result) && result.length > 0) {
            related_videos_dict['movie-series'] = result;
            related_videos_dict['movie-series'] = {
                'videos': result,
                'title': `movie series: "${vd.movie_series}"  (${result.length} videos)`,
            };
        }
    }

    if (vd.line) {
        const result = await $.get('/api/get/line/'+vd.line);
        if (Array.isArray(result) && result.length > 0) {
            related_videos_dict['line'] = result;
            related_videos_dict['line'] = {
                'videos': result,
                'title': `line: ${vd.line}  (${result.length} videos)`,
            };
        }
    }

    console.log(`loaded related videos in ${Math.floor((Date.now()-start))} ms`);


    /* STEP 2: request similar videos */

    const query_amount = 512
    const result = await $.get(`/api/query/get/similar-videos/${vd.hash}/0/${query_amount}`);
    let similar_videos = result.search_results;

    /* remove related videos from similar videos */
    const related_vid_hashes = new Set();
    for (let rel_obj of Object.values(related_videos_dict)) {
        for (let vid_obj of rel_obj.videos) {
            related_vid_hashes.add(vid_obj.hash);
        }
    }
    similar_videos = similar_videos.filter(vid => !related_vid_hashes.has(vid.hash));
    console.log('similar videos removed:', (query_amount-similar_videos.length));


    /* STEP 3: Render similar videos */
    const card_type = "search-result-card-default";  // TODO: Replace with local storage
    
    /* similar videos */
    const expand_results_func = await render_video_cards(
        similar_videos,
        similar_sec,
        8,
        '24rem',
        card_type,
        1,
    );
    $(similar_sec).find('#expand-results-button').on('click', expand_results_func);



    /* STEP 4: Get remaining related videos and render carousels */

    /* load from actors */
    // if (vd.actors.length > 1) {
    //     const query = _get_blank_query();
    //     query.actor = vd.actors.join(',');
    //     query.sortby = 'date_released';
    //     makeApiRequestPOST_JSON('/api/query/search-videos', query, (results) => {
    //         const videos = results.search_results;
    //         // configure_carousel(videos, video_data.hash, section,
    //             // 'from-actors', `with: ${video_data.actors.slice(0,-1).join(', ') + ' & ' + video_data.actors.slice(-1)}  (${videos.length} videos)`);
    //     });
    // }
    // await sleep(300);
    
    // /* load from actor & studio */
    // if (vd.primary_actors.length == 1 && vd.studio) {
    //     const query = _get_blank_query();
    //     query.actor = vd.primary_actors[0];
    //     query.studio = vd.studio;
    //     query.sortby = 'date_released';
    //     makeApiRequestPOST_JSON('/api/query/search-videos', query, (results) => {
    //         const videos = results.search_results;
    //         // configure_carousel(videos, video_data.hash, section,
    //             // 'from-actor-studio', `${query.actor} in ${query.studio} (${videos.length} videos)`);
    //     });
    // }


    /* render carousels */
    load_related_videos(
        related_videos_dict,
        related_sec,
        video_hash,
    )

}


/**
 * 
 * @param {Object} related_videos 
 * @param {HTMLElement} section 
 * @param {string} video_hash 
 */
async function load_related_videos(related_videos, section, video_hash) {

    if (Object.keys(related_videos).length === 0) {
        $(section).hide();
        return;
    }
    
    $(section).css('visibility', 'visible');

    /* render carousels */
    for (let [cls_, obj] of Object.entries(related_videos)) {
        configure_carousel(
            obj.videos,
            video_hash,
            section,
            cls_,
            obj.title,
        );
        await sleep(100);
    }

    /* Button event listeners*/
    const rel_vids_nav_buttons = $('.related-videos-nav button');
    const rel_vids_carousels = $('.carousel-container');
    rel_vids_nav_buttons.each((idx, button) => {
        button.onclick = () => {
            if (!button.classList.contains('selected') && !button.classList.contains('disabled')) {
                const ident = Array.from(button.classList).find(
                    cls => cls !== 'selected' && cls !== 'disabled'
                );
                rel_vids_nav_buttons.each((idx, butt) => { $(butt).removeClass('selected'); });
                rel_vids_carousels.each((idx, car) => { $(car).removeClass('shown'); });
                $('.related-videos-nav button.'+ident).addClass('selected');
                $('.carousel-container.'+ident).addClass('shown');
            }
        }
    });
    
}



//region - PRIVATE -----------------------------------------------------------------------------------------------------


function configure_carousel(videos, video_hash, section, identifier, title) {
    
    if (videos.length < 2) return;
    
    const carouselContainer = $(section).find('.carousel-container.'+identifier);
    const carousel = carouselContainer.find('.carousel');
    const button = $(section).find('.related-videos-nav button.'+identifier);

    carouselContainer.find('h3').text(title);

    button.removeClass('disabled');

    let carousel_content = '';
    for (let i = 0; i < 4; i++) {
        if (i < videos.length) {
            const result = videos[i];
            const highlighted = (result.hash === video_hash);
            carousel_content += /* html */`
                <search-result-card-default
                    highlighted = ${highlighted}
                    use_video_teasers = false
                    widthh = 32rem
                    video_hash =        "${result.hash}"
                    video_title =       "${result.title}"
                    actors =            "${result.actors}"
                    studio =            "${result.studio}"
                    line =              "${result.line}"
                    date_released =     "${result.date_released}"
                    year =              "${result.year}"
                    description =       "${result.description}"
                    collection =        "${result.collection}"
                    dvd_code =          "${result.dvd_code}"
                    duration =          "${result.duration}"
                    resolution =        "${result.resolution}"
                    fps =               "${result.fps}"
                    bitrate =           "${result.bitrate}"
                    date_added =        "${result.date_added}"
                    tags =              "${result.tags}"
                    filename =          "${result.filename}"
                ></search-result-card-default>
            `;
        }
    }
    
    carousel.append(carousel_content);
    
    /* buttons */

    // prev
    $(section).find('button.prev').on('mousedown', () => {
        if (button.hasClass('selected')) {
            // ...
        }
    });

    // next
    $(section).find('button.next').on('mousedown', () => {
        if (button.hasClass('selected')) {
            // ...
        }
    });
    
}


function _get_blank_query() {
    return {
        search_string: null,    // str,
        actor: null,            // str,
        studio: null,           // str,
        collection: null,       // str,
        include_terms: [],      // list[str],
        exclude_terms: [],      // list[str],
        date_added_from: null,      // str,
        date_added_to: null,        // str,
        date_released_from: null,   // str,
        date_released_to: null,     // str,
        only_favourites: false,     // bool,
        sortby: 'date_released',    // str|None,
        limit: 99,                // int,
        startfrom: 0,              // int,
    };
}




function _get_current_carousel_page(buttons) {


    
}
