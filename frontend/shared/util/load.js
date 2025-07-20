import '../../shared/web_components/search_result_cards/default_card.js'


const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));


/**
 * 
 * @param {Array} videos
 * @param {HTMLElement} container 
 * @param {number} load_amount 
 * @param {number} startfrom 
 * @returns Callback to add more results
 */
export async function render_video_cards(videos, container, load_amount, startfrom=0) {

    $(container).show();

    const card_options = _get_card_options();

    let videos_loaded = await render_video_cards_helper(
        videos,
        startfrom,
        load_amount,
        container,
        card_options,
    );

    return async () => {
        videos_loaded = await render_video_cards_helper(
            videos,
            videos_loaded,
            load_amount,
            container,
            card_options,
        );
    };
}

async function render_video_cards_helper(videos, start_idx, load_amount, container, card_options) {

    const videos_to_add = {}

    /* add placeholders */
    for (let i = start_idx; i < start_idx+load_amount; i++) {
        if (i >= videos.length) break;
        const placeholder_id = 'video_placeholder-'+i;
        videos_to_add[placeholder_id] = videos[i];
        $(container).find('.video-cards-styler').append( get_placeholder(placeholder_id, card_options.card_width) );
    }

    /* add videos */
    let videos_added = 0;
    for (let [ph_id, video] of Object.entries(videos_to_add)) {
        const card_html = get_video_card(video, card_options);
        $('#' + ph_id).replaceWith(card_html);
        videos_added++;
        await sleep(50);
    }

    return videos_added;
}



function get_video_card(vd, {card_width, card_type, use_video_teasers, aspect_ratio}) {
    return /* html */`
        <search-result-card-default
            use_video_teasers = ${use_video_teasers}
            highlighted = false
            use_video_teasers = false
            width = ${card_width}
            aspect_ratio = "${aspect_ratio}"
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
    `
}


function get_placeholder(id_, width) {
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
            ></div>
        </div>
    `;
}



function _get_card_options() {
    
    const card_options = {
        card_type: "default",
        card_width: null,
        aspect_ratio: null,
        use_video_teasers: (localStorage.getItem('use_video_teasers') == 'true'),
    }

    const card_size = localStorage.getItem('card_size') || 'medium';

    switch(card_size) {
        case "small":
            card_options.card_width = "20.5rem";
            card_options.aspect_ratio = "14/9";
            break;
        case "medium":
            card_options.card_width = "25rem";
            card_options.aspect_ratio = "16/9";
            break;
        case "large":
            card_options.card_width = "33rem";
            card_options.aspect_ratio = "18/9";
            break;
    }
    
    return card_options;
}


/* OLD */



/** 
 * @param {Object} results
 * @param {*} results_container
 */
export async function generate_results(results, results_container, card_type="search-result-card-default") {
    
    results_container.css('visibility', 'visible');
    
    // let html_content = '';
    // results.search_results.forEach( async (result, idx) => {
    for (let result of results.search_results) {
        let html_content = /* html */`
            <search-result-card-default
                highlighted = false
                use_video_teasers = false
                width = 24rem
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
        `
        results_container.find('.video-cards-styler').append(html_content)
        // console.log(`adding video card: ${result.hash}`);
        await sleep(75);
    };
    

}

