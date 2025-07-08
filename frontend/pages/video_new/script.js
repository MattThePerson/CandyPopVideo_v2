
/* IMPORTS */

import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET, makeApiRequestPOST } from '../../shared/util/request.js';
import { PassionPlayer } from '../../shared/libraries/PassionPlayer.js';
import { generate_results } from '../../shared/util/load.js';
import { configure_teaser_thumb_spritesheet } from '../../shared/util/vtt.js';
import '../../shared/web_components/search_result_cards/default_card.js'

injectComponents();



/* HANDLE RANDOM VIDEO REQUEST */

const urlParams = new URLSearchParams(window.location.search);

if (urlParams.get('random') || !urlParams.get('hash')) {
    console.log("Getting random video hash ...");
    const response = await fetch('/api/get/random-video-hash');
    const data = await response.json()
    const params = new URLSearchParams(location.search);
    params.set('hash', data.hash);
    location.replace(location.pathname + '?' + params.toString())
    await new Promise(() => {});
}



//region - FUNCTIONS ---------------------------------------------------------------------------------------------------


function load_similar_videos(results_container, video_hash, start_idx, load_amount) {
    makeApiRequestGET('/api/query/get/similar-videos', [video_hash, start_idx + 1, load_amount], search_results => {
        console.log(results_container);
        generate_results(search_results, results_container);
    });
    return start_idx + load_amount
};


function hydrate_preview_info(selector, data) {

    const container = $(selector);

    container.find('.scene_title').text(data.scene_title);
    container.find('.date_released').text(data.date_released);
    
    /* append studios */
    for (let x of [data.studio, data.line]) {
        if (x) {
            container.find('.studios-container').append(`
                <a class="studio" href="/pages/search/page.html?studio=${x}">
                    ${x}
                </a>
            `);
        }
    }

    for (let x of data.performers) {
        container.find('.performers-container').append(/* html */`
            <a class="performer" href="/pages/search/page.html?performer=${x}">
                ${x}
            </a>
        `);
        
    };
}


function hydrate_about_section(selector, data) {

    const section = $(selector);

    /* left side */
    section.find('.scene_title').text( data.scene_title )
    section.find('.resolution').text( data.resolution )
    section.find('.bitrate').text( data.bitrate )
    section.find('.fps').text( data.fps )
    section.find('.duration').text( data.duration )
    section.find('.collection').text( data.collection )
    section.find('.date_released').text( data.date_released )
    
    /* append studios */
    for (let x of [data.studio, data.line]) {
        if (x) {
            section.find('.studios-container').append(`
                <div class="studio">${x}</div>
            `);
        }
    }

    data.performers.forEach(name => {
        const card_id = 'performer-card_' + name.toLowerCase().replace(/ /g, '-');
        section.find('.performer-cards-bar').append(get_performer_card(name, card_id));
        // makeApiRequestGET('/api/get/performer-data', [name], perf_data => {
        //     // TODO: get performer age ITS
        //     $('#' + card_id).find('age').text(perf_data.age + ' y/o ITS');
        //     $('#' + card_id).find('scene_count').text(perf_data.scene_count + ' scenes');
        // });
    });
    
    
}

function get_performer_card(name, card_id) {
    return /* html */`
        <div id="${card_id}" class="performer-card">
            <img src="" alt="">
            <h3 class="name">${name}</h3>
            <div class="age">29 y/o ITS</div>
            <div class="scene-count">69 scenes</div>
        </div>
    `;
}


//region - EVENT LISTENERS ---------------------------------------------------------------------------------------------


//region - GLOBAL VARIABLES --------------------------------------------------------------------------------------------



//region - BACKEND REQUEST ---------------------------------------------------------------------------------------------

const video_hash = urlParams.get('hash');

console.log(video_hash);

// GET VIDEO

if (video_hash === null) {
    throw new TypeError("Expected a non-null value");
}



makeApiRequestGET('/api/get/video-data', [video_hash], videodata => {

    console.log('videodata:', videodata);
    
    document.title = videodata.performers.join(', ') + ' in ' + videodata.scene_title;

    /* - Initialize preview pane -------------------------------------------- */

    const preview_container = $('.video-preview-container');

    preview_container.find('img.poster').get(0).src = '/media/get/poster-large/' + video_hash + '?t=' + Date.now()
    
    makeApiRequestGET('/media/ensure/teaser-large', [video_hash], () => {
        const teaser_video = preview_container.find('video').get(0);
        teaser_video.src = `/static/preview-media/0x${video_hash}/teaser_large.mp4`;
        // teaser_video.pause();
        preview_container.on('click', () => {
            if (teaser_video.paused) teaser_video.play(); else teaser_video.pause();
        })
    });

    hydrate_preview_info('.video-preview-container .info-container', videodata);

    makeApiRequestGET('/media/ensure/teaser-thumbs-large', [video_hash], () => {
        const teaser_thumbs = preview_container.find('img.teaser').get(0);
        const teaser_thumbs_src = `/static/preview-media/0x${video_hash}/teaser_thumbs_large.jpg`;
        configure_teaser_thumb_spritesheet(teaser_thumbs_src, teaser_thumbs, preview_container.get(0));
    });

    /* toggle teaser mode */
    $('.toggle-teaser-mode-button').on('click', (e) => {
        e.stopPropagation();
        preview_container.find('video').toggleClass('hidden');
        preview_container.find('img.teaser').toggleClass('hidden');
    });

    /* play */
    $('.play-button').on('click', (e) => {
        e.stopPropagation();
        // toggle preview and video panels ...
    });


    /* - Initialize video player -------------------------------------------- */

    console.log('initializing player ...')
    
    // const player = new PassionPlayer({
    //     player_id: 'video-container',
    //     src: '/media/get/video/' + video_hash,
    //     title: videodata.scene_title,
    //     styles: '/shared/libraries/PassionPlayer.css',
    //     markers_get: '/api/interact/markers/get/' + video_hash,
    //     markers_post: '/api/interact/markers/update/' + video_hash,
    // });
    

    /* - Hydrate about section ---------------------------------------------- */

    hydrate_about_section('.video-about-section', videodata);


    /* - Load related videos ------------------------------------------------ */


    
    /* - Load similar videos -------------------------------------------- */

    const similar_videos_load_amount = 8;
    let similar_videos_loaded = 0;
    const similar_videos_section = $('.similar-videos-section');
    
    // similar_videos_loaded = load_similar_videos(similar_videos_section, video_hash, similar_videos_loaded, similar_videos_load_amount);
    // $('#expand-results-button').click = () => {
    //     similar_videos_loaded = load_similar_videos(similar_videos_section, video_hash, similar_videos_loaded, similar_videos_load_amount);
    // };

});


/* VIDEO INTERACTIONS */

// makeApiRequestGET('/api/interact/get', [video_hash], video_interactions => {

//     console.log('video_interactions:', video_interactions);
    
//     // configure favourites button
//     favouritesButton.onclick = (args) => {
//         if (video_interactions.is_favourite) {
//             console.log("removing favourite: ", video_hash);
//             makeApiRequestPOST('/api/interact/favourites/remove', [video_hash], () => {
//                 toggle_favourites_button_OFF(favouritesButton);
//                 video_interactions.is_favourite = false;
//             });
//         } else {
//             console.log("adding favourite: ", video_hash);
//             makeApiRequestPOST('/api/interact/favourites/add', [video_hash], () => {
//                 toggle_favourites_button_ON(favouritesButton);
//                 video_interactions.is_favourite = true;
//             });
//         }
//     };

//     toggle_favourites_button_OFF(favouritesButton);
//     if (video_interactions.is_favourite) {
//         toggle_favourites_button_ON(favouritesButton);
//     }
    
// });

