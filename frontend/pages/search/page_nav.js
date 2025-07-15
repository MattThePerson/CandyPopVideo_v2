

/**
 * 
 * @param {number} videos_filtered_count 
 * @param {number} time_taken 
 * @param {*} search_query 
 */
export function configure_page_nav(videos_filtered_count, time_taken, search_query) {
    const amount_of_results = videos_filtered_count;
    const number_of_pages = Math.max(1, Math.floor((amount_of_results-1) / search_query.limit) + 1);
    
    /** @type {HTMLElement} */
    const page_number = document.querySelector('#search-page-info .page-number')
    if (page_number) {
        page_number.innerText += ' of ' + number_of_pages + ' (' + amount_of_results + ' search results, took ' + time_taken + ' seconds)';
    }
    
    const current_page = Math.floor(search_query.startfrom / search_query.limit);
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

    /** @type {HTMLInputElement} */
    const pageNumberInput = document.querySelector('.page-number-input');
    pageNumberInput.addEventListener('keydown', (/** @type {KeyboardEvent} */ event) => {
        console.log('Keydown in input');
        if (event.key === 'Enter' && pageNumberInput.value != '') {
            let n = parseInt(pageNumberInput.value);
            n = Math.max(0, n);
            n = Math.min(number_of_pages, n);
            switch_to_page(n);
        }
    });
}

function switch_to_page(n) {
    console.log("Switching to page: " + n)
    let url = new URL(window.location.href);
    if (url.searchParams.has('page')) {
        url.searchParams.set('page', n);
    } else {
        url.searchParams.append('page', n);
    }
    window.location.href = url.toString();
}


function getPageNavNumbers(current_page, amount_of_pages, max_buttons) {
    if (amount_of_pages == 1) 
        return [1];
    if (current_page > amount_of_pages) current_page = amount_of_pages;
    if (current_page < 1)               current_page = 1;

    let pages = [];
    let i = current_page;
    pages.push(i);
    let disp = 1;
    while ( pages.length < Math.min(amount_of_pages, max_buttons) ) {
        let hold = pages.length;
        let lo = i - disp;
        let hi = i + disp;
        if (lo > 0)                 pages.push(lo);
        if (hi <= amount_of_pages)  pages.push(hi);
        if (pages.length == hold)
            break;
        disp += 1;
    }
    pages.sort((a,b) => (a - b));
    pages[0] = 1;
    pages[pages.length-1] = amount_of_pages;
    if ( Math.abs(pages[0]-pages[1]) > 1 )  pages[1] = -1;
    if ( Math.abs(pages[pages.length-1]-pages[pages.length-2]) > 1 ) pages[pages.length-2] = -1;
    return pages;
}

