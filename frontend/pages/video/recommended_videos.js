import { render_video_cards } from "../../shared/util/load.js";


const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));


// #region - PUBLIC ----------------------------------------------------------------------------------------------------

/**
 * 
 * @param {Object} vd 
 * @param {HTMLElement} related_sec 
 * @param {HTMLElement} similar_sec 
 */
export async function load_recommended_videos(vd, related_sec, similar_sec) {
    
    
    /* GET INITIAL RELATED VIDEOS */

    let related_videos_dict = {};

    /* movie series */
    if (vd.movie_series) {
        const result = await $.get('/api/get/movie-series/'+vd.movie_series);
        if (Array.isArray(result) && result.length > 1) {
            related_videos_dict['movie-series'] = {
                videos: result,
                title: `movie series: "${vd.movie_series}"`,
            };
        }
    }

    /* movie */
    if (vd.movie_title) {
        const result = await $.get('/api/get/movie/'+vd.movie_title);
        if (Array.isArray(result) && result.length > 1) {
            related_videos_dict['movie'] = {
                videos: result,
                title: `movie title: "${vd.movie_title}"`,
            };
        }
    }
    await sleep(100);

    /* from line */
    if (vd.line) {
        const result = await $.get('/api/get/line/'+vd.line);
        if (Array.isArray(result) && result.length > 1) {
            related_videos_dict['from-line'] = {
                videos: result,
                title: `line: ${vd.line}`,
            };
        }
    }
    await sleep(100);
    
    /* RENDER CAROUSELS */
    load_related_videos(
        related_videos_dict,
        related_sec,
        vd.hash,
    )


    /* - GET SIMILAR VIDEOS --------------------------------------------------------------------- */

    const types_to_ignore = ['movie-series', 'from-line'];
    const videos_to_ignore = types_to_ignore
                                .filter(k => k in related_videos_dict)
                                .map(k => related_videos_dict[k].videos).flat();
    const similar_videos = await get_filtered_similar_videos(
        videos_to_ignore,
        vd.hash,
    );
    const expand_results_func = await render_video_cards(
        similar_videos,
        similar_sec,
        8,
        1,
    );
    $(similar_sec).find('#expand-results-button').on('click', expand_results_func);
    await sleep(100);



    /* GET REMAINING RELATED VIDEOS */
    
    // @ts-ignore (complains for some reason)
    related_videos_dict = {};
    
    /* from actors */
    if (vd.actors.length > 1) {
        const result = await _get_videos_from_actors(vd);
        if (Array.isArray(result) && result.length > 1) {
            const actors_str = vd.actors.slice(0,-1).join(', ') + ' & ' + vd.actors.slice(-1);
            related_videos_dict['from-actors'] = {
                'videos': result,
                'title': `with: ${actors_str}`,
            };
        }
    }
    await sleep(100);
    
    /* from actor-studio */
    if (vd.primary_actors.length == 1 && vd.studio) {
        const result = await _get_videos_from_actor_studio(vd);
        if (Array.isArray(result) && result.length > 1) {
            related_videos_dict['from-actor-studio'] = {
                'videos': result,
                'title': `${vd.primary_actors[0]} in ${vd.studio}`,
            };
        }
    }

    /* RENDER REMAINING RELATED VIDEOS */
    load_related_videos(
        related_videos_dict,
        related_sec,
        vd.hash,
    )

}


// #endregion

// #region - RELATED VIDEOS --------------------------------------------------------------------------------------------

/**
 * 
 * @param {Object} related_videos 
 * @param {HTMLElement} section 
 * @param {string} video_hash 
 */
async function load_related_videos(related_videos, section, video_hash) {

    if (Object.keys(related_videos).length === 0) return;
    
    $(section).show();

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

    /* prev/next buttons */
    $(section).find('button.prev').on('mousedown', () => {
        const shown_carousel_container = $('.carousel-container.shown').get(0);
        shown_carousel_container.scrollTo({
            left: shown_carousel_container.scrollLeft - 800,
            behavior: 'smooth'
        });
    });

    $(section).find('button.next').on('mousedown', () => {
        const shown_carousel_container = $('.carousel-container.shown').get(0);
        shown_carousel_container.scrollTo({
            left: shown_carousel_container.scrollLeft + 800,
            behavior: 'smooth'
        });
    });
    
    /* switch to first loaded carousel */
    if ($('.carousel-container.shown').length === 0) {
        const first_non_disabled_button = $('.related-videos-nav button:not(.disabled)');
        first_non_disabled_button.get(0).dispatchEvent(
            new Event('click')
        );
    }
    
}


// #region - VIDEO GETTERS ---------------------------------------------------------------------------------------------


async function get_filtered_similar_videos(videos_to_ignore, target_video_hash) {
    const query_amount = 512;
    const result = await $.get(`/api/query/get/similar-videos/${target_video_hash}/0/${query_amount}`);
    let similar_videos = result.search_results;

    /* remove related videos from similar videos */
    const related_vid_hashes = new Set();
    for (let vid_obj of videos_to_ignore) {
        related_vid_hashes.add(vid_obj.hash);
    }
    similar_videos = similar_videos.filter(vid => !related_vid_hashes.has(vid.hash));
    console.debug('similar videos removed:', (query_amount-similar_videos.length));
    return similar_videos;
}


async function _get_videos_from_actors(vd) {
    const query = _get_blank_query();
    query.actor = vd.actors.join(',');
    query.sortby = 'date_released';
    const response = await $.ajax({
        url: '/api/query/search-videos',
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(query),
    })
    return response.search_results;
}

async function _get_videos_from_actor_studio(vd) {
    const query = _get_blank_query();
    query.actor = vd.primary_actors[0];
    query.studio = vd.studio;
    query.sortby = 'date_released';
    const response = await $.ajax({
        url: '/api/query/search-videos',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(query),
    })
    return response.search_results;
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


// #endregion

// #region - CAROUSEL --------------------------------------------------------------------------------------------------


function configure_carousel(videos, target_video_hash, section, identifier, title) {
    
    const carouselContainer = $(section).find('.carousel-container.'+identifier);
    const carousel = carouselContainer.find('.carousel');
    const nav_button = $(section).find('.related-videos-nav button.'+identifier);

    carouselContainer.find('h3').text(title);
    nav_button.removeClass('disabled');
    nav_button.get(0).innerText += ` (${videos.length})`;

    const card_width = '23rem';
    
    /* add placeholders */
    const card_html_store = {};
    let highlighted_id;
    let carousel_content = '';
    videos.forEach((video, idx) => {
        const placeholder_id = identifier + '-placeholder-' + idx;
        carousel_content += _get_placeholder_html(placeholder_id, card_width, video.title);
        card_html_store[placeholder_id] = video;
        if (video.hash === target_video_hash) {
            highlighted_id = placeholder_id;
        }
    });
    carousel.append(carousel_content);
    
    /* render target card */
    const card_html = _get_video_card_html({
        vd: card_html_store[highlighted_id],
        card_width: card_width,
        class_list: "target-video",
        is_highlighted: true,
    });
    $('#'+highlighted_id).replaceWith(card_html);

    /* render cards besides target card */
    const target_card_idx = Object.keys(card_html_store).indexOf(highlighted_id);
    const side_card_ids = _get_index_neighbours(
        Object.keys(card_html_store),
        target_card_idx,
        2,
    )
    for (let ph_id of side_card_ids) {
        const card_html = _get_video_card_html({
            vd: card_html_store[ph_id],
            card_width: card_width,
        });
        $('#'+ph_id).replaceWith(card_html);
    }
    
    /* nav button event listener */
    nav_button.on('click', () => {
        if (!nav_button.hasClass('selected')) {
            $('.related-videos-nav button').each((_, butt) => butt.classList.remove('selected') );
            $('.carousel-container')       .each((_, car) => car.classList.remove('shown') );
            nav_button.addClass('selected');
            carouselContainer.addClass('shown');
            // if (!carouselContainer.hasClass('first-switch')) {
            //     _carousel_first_load(carouselContainer, card_html_store);
            //     carouselContainer.addClass('first-switch');
            // }
        }
    });

    nav_button.one('click', () => {
        _carousel_first_load(carouselContainer, card_html_store, card_width);
    })
    
}


function _get_placeholder_html(id_, width, title) {
    return /* html */ `
        <div
            id="${id_}"
            class="placeholder"
            style="
                background: black;
                border-radius: 5px;
                overflow: hidden;
                height: fit-content;
                padding-bottom: 6rem;
                margin-bottom: 2px;
                width: ${width};
            "
        >
            <div
                class="blank-thumbnail"
                style="
                    width: 100%;
                    aspect-ratio: 16/9;
                    background: #222;
                "
            >${title}</div>
        </div>
    `;
}


function _get_video_card_html({vd, card_width, class_list="", is_highlighted=false}) {
    return /* html */`
        <search-result-card-default
            class = "${class_list}"
            highlighted = ${is_highlighted}
            use_video_teasers = false
            width = ${card_width}
            video_hash =        "${vd.hash}"
            video_title =       "${vd.title}"
            actors =            "${vd.actors}"
            studio =            "${vd.studio}"
            line =              "${vd.line}"
            date_released =     "${vd.date_released}"
            year =              "${vd.year}"
            description =       "${vd.description}"
            collection =        "${vd.collection}"
            dvd_code =          "${vd.dvd_code}"
            duration =          "${vd.duration}"
            resolution =        "${vd.resolution}"
            fps =               "${vd.fps}"
            bitrate =           "${vd.bitrate}"
            date_added =        "${vd.date_added}"
            tags =              "${vd.tags}"
            filename =          "${vd.filename}"
        ></search-result-card-default>
    `;
}


function _carousel_first_load(carouselContainer, card_html_store, card_width) {

    /* determine initial offset */
    const cont_rect =     carouselContainer.get(0).getBoundingClientRect();
    const carousel_rect = carouselContainer.find('.carousel').get(0).getBoundingClientRect();
    const card_rect =     carouselContainer.find('.target-video').get(0).getBoundingClientRect();
    const x_offset = card_rect.left - carousel_rect.left - cont_rect.width/2 + card_rect.width/2;
    carouselContainer.get(0).scrollLeft = x_offset;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                observer.unobserve(entry.target);
                const card_html = _get_video_card_html({
                    vd: card_html_store[entry.target.id],
                    card_width: card_width,
                })
                $(entry.target).replaceWith(card_html);
            }
        });
        
    }, {
        root: carouselContainer.get(0),
        rootMargin: '0px',
        threshold: 0.1,
    })

    carouselContainer.find('.placeholder').each((idx, placeholder) => {
        observer.observe(placeholder);
    })

    
}


// #endregion


// #region - HELPERS ---------------------------------------------------------------------------------------------------

function _get_index_neighbours(array, idx, num=2) {
    const neighs = [];
    for (let d = 1; d <= num; d++) {
        for (let diff of [idx-d, idx+d]) {
            if (array[diff]) {
                neighs.push(array[diff]);
            }
        }
    }
    return neighs;
}

