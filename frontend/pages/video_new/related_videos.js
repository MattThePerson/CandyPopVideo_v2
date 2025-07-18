import { makeApiRequestPOST_JSON } from "../../shared/util/request.js"


const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

//region - PUBLIC ------------------------------------------------------------------------------------------------------

export async function load_related_videos(video_data, section) {
    
    /* load movie series */
    if (video_data.movie_title || video_data.movie_series) {
        get_movie_series(video_data.movie_title, video_data.movie_series, (videos, title) => {
            configure_carousel(videos, video_data.hash, section,
                'movie-series', `movie series: "${title}"  (${videos.length} videos)`);
        });
    }
    await sleep(300);

    /* load from actors */
    if (video_data.actors.length > 1) {
        const query = _get_blank_query();
        query.actor = video_data.actors.join(',');
        query.sortby = 'date_released';
        makeApiRequestPOST_JSON('/api/query/search-videos', query, (results) => {
            const videos = results.search_results;
            configure_carousel(videos, video_data.hash, section,
                'from-actors', `with: ${video_data.actors.slice(0,-1).join(', ') + ' & ' + video_data.actors.slice(-1)}  (${videos.length} videos)`);
        });
    }
    await sleep(300);
    
    /* load from actor & studio */
    if (video_data.primary_actors.length == 1 && video_data.studio) {
        const query = _get_blank_query();
        query.actor = video_data.primary_actors[0];
        query.studio = video_data.studio;
        query.sortby = 'date_released';
        makeApiRequestPOST_JSON('/api/query/search-videos', query, (results) => {
            const videos = results.search_results;
            configure_carousel(videos, video_data.hash, section,
                'from-actor-studio', `${query.actor} in ${query.studio} (${videos.length} videos)`);
        });
    }
    await sleep(300);

    /* load line videos */
    if (video_data.line) {
        $.get('/api/get/line/'+video_data.line, (videos, status) => {
            if (status === 'success') {
                configure_carousel(videos, video_data.hash, section,
                    'from-line', `line: ${video_data.line}  (${videos.length} videos)`);
            }
        })
    }

    
    /* EVENT LISTENERS */

    const rel_vids_nav_buttons = $('.related-videos-nav button');
    const rel_vids_carousels = $('.carousel-container');
    rel_vids_nav_buttons.each((idx, button) => {
        button.onclick = () => {
            if (!button.classList.contains('selected') && !button.classList.contains('disabled')) {
                const ident = Array.from(button.classList).find(
                    cls => cls !== 'selected' && cls !== 'disabled'
                );
                // add selected to current button
                rel_vids_nav_buttons.each((idx, butt) => { $(butt).removeClass('selected'); });
                $('.related-videos-nav button.'+ident).addClass('selected');
                
                rel_vids_carousels.each((idx, car) => { $(car).removeClass('shown'); });
                $('.carousel-container.'+ident).addClass('shown');
            }
        }
    });

}


//region - PRIVATE -----------------------------------------------------------------------------------------------------


function configure_carousel(videos, video_hash, section, identifier, title) {
    
    if (videos.length < 2) return;
    
    const carouselContainer = section.find('.carousel-container.'+identifier);
    const carousel = carouselContainer.find('.carousel');
    const button = section.find('.related-videos-nav button.'+identifier);

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
    section.find('button.prev').on('mousedown', () => {
        if (button.hasClass('selected')) {
            // ...
        }
    });

    // next
    section.find('button.next').on('mousedown', () => {
        if (button.hasClass('selected')) {
            // ...
        }
    });
    
}



async function get_movie_series(movie_title, movie_series, callback) {

    let req, param;
    if (movie_series) {
        param = movie_series;
        req = '/api/get/movie-series';
    } else {
        param = movie_title;
        req = '/api/get/movie';
    }

    const res = await $.get(req + '/' + param);

    callback(res, param);
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
