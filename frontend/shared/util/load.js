



export function generate_results(results, results_container, card_type="search-result-card-default", page_nav=null) {
    
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
    

    /* Configure page nav */
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

