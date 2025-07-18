import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET, makeApiRequestPOST } from '../../shared/util/request.js';
import { generate_results } from '../../shared/util/load.js';
import { load_video_player } from './player_old.js';
import { load_related_videos } from './related_videos.js';

injectComponents();


const urlParams = new URLSearchParams(window.location.search);


//region - HANDLE RANDOM VIDEO REQUEST ---------------------------------------------------------------------------------

if (urlParams.get('random') || !urlParams.get('hash')) {
    console.log("Getting random video hash ...");
    makeApiRequestGET('/api/get/random-video-hash', [], (arg) => {
        const params = new URLSearchParams(location.search);
        params.set('hash', arg.hash);
        location.replace(location.pathname + '?' + params.toString())
    });
}

let autoplayVideo = false;
if (urlParams.get('autoplay'))
    autoplayVideo = true;


//region - FUNCTIONS ---------------------------------------------------------------------------------------------------


function hydrate_info_section(section, video_data) {
    
    section.find('.title-bar h1').text( video_data.title );
    section.find('.year').text( video_data.date_released );

    
    section.find('.collection').text( video_data.collection );
    section.find('.collection').attr('href', `/pages/search/page.html?collection=${video_data.collection}`)

    // add studios
    const studios_cont = section.find('.studios-container');
    [video_data.studio, video_data.line].forEach((studio, idx) => {
        if (studio) {
            if (idx !== 0) studios_cont.append(`<div></div>`);
            studios_cont.append(/* html */`
                <a href="/pages/search/page.html?studio=${studio}">${studio}</a>
            `);
        }
    })
    
    // add actors
    const actors_cont = section.find('.actors-container');
    video_data.actors.forEach((actor, idx) => {
        const actor_id = 'actor_link-' + actor.replace(/ /g, '_');
        if (idx !== 0) actors_cont.append('<div></div>');
        actors_cont.append(/* html */`
            <a id="${actor_id}" href="/pages/search/page.html?actor=${actor}">${actor}</a>
        `);

        /* request */
        $.get('/api/get/actor/'+actor, (data, status, response) => {
            if (response.status === 200) {
                const age_its = get_year_difference_between_dates(data.date_of_birth, video_data.date_released);
                if (age_its) {
                    document.getElementById(actor_id).innerText += ` (${age_its} y/o ITS)`
                }
            }
        })
    })


    
    
    /* event listeners */

    /* check favourite */
    const is_fav_button = section.find('button.is-fav-button');
    $.get(`/api/interact/favourites/check/${videoHash}`, (data, status) => {
        // console.log(status);
        if (status === 'success') {
            is_fav_button.addClass('loaded');
            if (data.is_favourite) {
                is_fav_button.addClass('is-fav');
            }
            // add event listeners
            is_fav_button.on('click', () => {
                let change_favourite_route;
                if (is_fav_button.hasClass('is-fav')) {
                    change_favourite_route = `/api/interact/favourites/remove/${videoHash}`;
                } else {
                    change_favourite_route = `/api/interact/favourites/add/${videoHash}`;
                }
                $.post(change_favourite_route, (data, status) => {
                    if (status === 'success') {
                        is_fav_button.toggleClass('is-fav');
                    }
                });
            });
        }
    });
    
}


function get_video_page_title(video_data)  {
    let title = video_data.primary_actors.join(', ');
    if (video_data.studio) {
        title += ` - ${video_data.studio}`;
    }
    title += ` - ${video_data.title}`;
    return title;
}

function toggle_favourites_button_ON(butt) {
    favouritesButton.innerText = 'REMOVE FAV';
    favouritesButton.style.background = 'red';
}

function toggle_favourites_button_OFF(butt) {
    favouritesButton.innerText = 'ADD FAV';
    favouritesButton.style.background = 'orange';
}


function get_year_difference_between_dates(date1, date2) {
    if (date1 === null || date2 === null) {
        return null;
    }
    const a = Date.parse(date1);
    const b = Date.parse(date2);
    if (isNaN(a) || isNaN(b)) {
        return null;
    }
    return Math.floor((b-a) / (1000 * 60 * 60 * 24 * 365))
}



//region - HELPER FUNCTIONS --------------------------------------------------------------------------------------------

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));


function _format_seconds(seconds) {

    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor( (seconds-hours*3600) / 60 );
    const secs = Math.floor( seconds - hours*3600 - mins*60 );

    if (hours > 0) {
        return `${hours} hours ${mins} mins ${secs} secs`;
    } else if (mins > 0) {
        return `${mins} mins ${secs} secs`;
    } else {
        return `${secs} secs`;
    }
    
}




//region - GLOBAL VARIABLES --------------------------------------------------------------------------------------------

let favouritesButton = document.getElementById('add-favourite-button')



//region - BACKEND REQUEST ---------------------------------------------------------------------------------------------

const videoHash = urlParams.get('hash');
console.log("Video hash: " + videoHash);

if (videoHash != null) {

    /* - video data --------------------------------------------------------- */

    makeApiRequestGET('/api/get/video-data', [videoHash], async (videodata) => {
        console.log('videodata:', videodata);
        
        document.title = get_video_page_title(videodata);
        
        /* load video player */
        load_video_player(videoHash, videodata, urlParams);
        
    
        /* Hydrate video about section */
        const info_section = $('section.video-info-section');
        hydrate_info_section(info_section, videodata);
    

        /* load similar videos */
        const load_similar_videos = (results_container, video_hash, start_idx, load_amount) => {
            makeApiRequestGET('/api/query/get/similar-videos', [video_hash, start_idx + 1, load_amount], search_results => {
                generate_results(search_results, results_container);
            });
            return start_idx + load_amount;
        };
        
        const similar_videos_load_amount = 8;
        let similar_videos_loaded = 0;
        
        const results_container = $('.similar-videos-section');
        similar_videos_loaded = load_similar_videos(results_container, videoHash, similar_videos_loaded, similar_videos_load_amount);
        document.getElementById('expand-results-button').addEventListener('click', () => {
            similar_videos_loaded = load_similar_videos(results_container, videoHash, similar_videos_loaded, similar_videos_load_amount);
        });

        
        /* load recommended videos */
        await sleep(1000);
        const related_videos_section = $('section.related-videos-section');
        load_related_videos(videodata, related_videos_section);
        
        
        
    });

    
    /* - video interactions ------------------------------------------------- */

    makeApiRequestGET('/api/interact/get', [videoHash], vi => {

        console.log('video_interactions:', vi);
        
        $('.viewtime').text('viewtime: ' + _format_seconds(vi.viewtime));
        
        const likes_button = $('.likes-button');
        likes_button.text(`${vi.likes} likes`);
        likes_button.on('click', () => {
            $.post('/api/interact/likes/add/'+videoHash, (data, status) => {
                if (status === 'success') {
                    likes_button.text(`${data.likes} likes`);
                }
            })
        })
        
    });
    
}
