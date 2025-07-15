import '../../shared/web_components/search_result_cards/default_card.js'


/**
 * @param {Object} results
 * @param {*} results_container
 */
export function generate_results(results, results_container, card_type="search-result-card-default") {
    
    results_container.css('visibility', 'visible');
    
    let html_content = '';
    results.search_results.forEach( (result) => {
        html_content += /* html */`
            <search-result-card-default
                highlighted = false
                use_video_teasers = false
                widthh = 32rem
                video_hash =        "${result.hash}"
                title =             "${result.title}"
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
    });
    results_container.find('.video-cards-styler').append(html_content)
    

}

