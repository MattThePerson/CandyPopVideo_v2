

const searchPanel = document.getElementById('search-panel');
const searchButton = document.getElementById('search-button');
const onlyFavsCheckbox = document.querySelector('input.only-favs');

/* FUNCTIONS */

function initiate_search(searchPanel) {
    let params = new URLSearchParams();
    if (urlParams.get('sort-by')) {
        params.set('sort-by', urlParams.get('sort-by'));
    }
    for (let pkey of ['query', 'performer', 'studio', 'collection', 'date-added-from', 'date-added-to', 'date-released-from', 'date-released-to', 'include-terms']) {
        let selector = `.${pkey}-input input`;
        try {
            let value = searchPanel.querySelector(selector).value;
            value = value.trim().replace(/\s+/g, ' ');
            if (value != '') {
                params.set(pkey, value);
                console.log(selector);
            }
        } catch {}
    }
    if (onlyFavsCheckbox.checked) {
        params.set('only-favs', true);
    }
    if (params.size > 0) {
        window.location.href = window.location.pathname + '?' + params.toString();
    } else {
        console.log("No search parameters given")
    }
}

function get_search_page_title(urlParams) {
    let arr = [];
    for (let param of ['query', 'performer', 'studio', 'collection']) {
        if (urlParams.get(param)) {
            arr.push(urlParams.get(param));
        }
    }

    return arr.join(', ') + ' SEARCH RESULTS';
}


function highlight_sort_button(sortBy) {
    let type = 'desc';
    if (sortBy.includes('asc')) {
        type = 'asc';
    }
    let buttonGroup = document.getElementById(sortBy.replace('-'+type, '') + '-button-group');
    buttonGroup.querySelector('.main').classList.add('selected');
    if (sortBy != 'random') {
        buttonGroup.querySelector('.' + type).classList.add('selected');
    }
}


function isPerformerPage(query) {
    return (query.actor != null && query.studio == null);
}


/* EVENT LISTENERS */

searchButton.addEventListener('click', arg => {
    initiate_search(searchPanel);
});

document.querySelectorAll('#search-panel .search-input').forEach(inputElement => {
    inputElement.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            initiate_search(searchPanel);
        }
    });
});

// sort-by buttons
for (let button_group of searchPanel.querySelectorAll('.sort-panel .button-group')) {
    let sort_type = button_group.id.replace('-button-group', '');
    let main = button_group.querySelector('.main');
    let asc = button_group.querySelector('.asc');
    let desc = button_group.querySelector('.desc');
    main.addEventListener('click', e => {
        let sort_by_arg = null;
        if (sort_type == 'random') {
            sort_by_arg = sort_type;
        } else {
            if (main.classList.contains('selected')) {
                if (desc.classList.contains('selected'))
                    sort_by_arg = sort_type + '-asc';
                else
                    sort_by_arg = sort_type + '-desc';
            } else {
                sort_by_arg = sort_type + '-desc';
                if (sort_type == 'filename' || sort_type == 'title' || sort_type == 'studio')
                    sort_by_arg = sort_by_arg.replace('desc', 'asc');
            }
        }
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('sort-by', sort_by_arg);
        urlParams.delete('page');
        window.location.href = window.location.pathname + '?' + urlParams.toString();
    });
    if (sort_type != 'random') {
        asc.addEventListener('click', e => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('sort-by', sort_type + '-asc');
            urlParams.delete('page');
            window.location.href = window.location.pathname + '?' + urlParams.toString();
        });
        desc.addEventListener('click', e => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('sort-by', sort_type + '-desc');
            urlParams.delete('page');
            window.location.href = window.location.pathname + '?' + urlParams.toString();
        });
    }
}


/* API CALLS */

document.title = get_search_page_title(urlParams);

const pageNumber = parseInt(urlParams.get('page')) || 1;
document.querySelector('#search-page-info .page-number').innerText = 'Page ' + (pageNumber);

const search_results_amount = urlParams.get('results-amount') || 24;
const search_results_start_index = search_results_amount * (pageNumber-1);

let query = { limit: search_results_amount, startfrom: search_results_start_index };

for (let key of ['query', 'performer', 'studio', 'collection', 'date-added-from', 'date-added-to', 'date-released-from', 'date-released-to', 'include-terms', 'exclude-terms']) {
    if (urlParams.get(key)) {
        try {
            searchPanel.querySelector(`.${key}-input input`).value = urlParams.get(key);
        } catch {
            console.log('No such element: ', `.${key}-input input`);
        }
        let query_key = key.replace(/-/g, '_');
        if (key == 'performer') {
            query_key = 'actor'
        } else if (key == 'query') {
            query_key = 'search';
        }
        query[query_key] = urlParams.get(key);
    }
}

if (urlParams.get('sort-by')) {
    query['sort_by'] = urlParams.get('sort-by');
    highlight_sort_button(urlParams.get('sort-by'));
} else {
    highlight_sort_button('date-added-desc');
}

if (urlParams.get('only-favs')) {
    query.only_favourites = true;
    onlyFavsCheckbox.checked = true;
}

console.log('Query: ', query);

let use_custom_thumbnails = window.location.pathname.includes('listPage.html');

if (urlParams.size > 0) {
    
    makeApiRequestGET_JSON('search-videos', query, search_results => {
        generate_results(search_results, {generate_nav : true}, use_custom_thumbnails);
        
        if (query.actor) {
            console.log('Making performer panel');
            makeApiRequestGET('get-similar-performers', [query.actor], performers => {
                if (performers) {
                    console.log('similar performers:', performers);
                    const modelStudioPanel = document.getElementById('model-studio-panel');
                    modelStudioPanel.style.display = 'flex';
                    modelStudioPanel.querySelector('.focus-performer').innerText = query.actor;
                    for (let i = 1; i < 12; i++) {
                    // for (let perf_data of performers) {
                        const perf_data = performers[i];
                        const newEl = document.createElement('a');
                        newEl.href = 'searchPage.html?' + (new URLSearchParams({'performer': perf_data.name})).toString();
                        newEl.innerText = perf_data.name;
                        modelStudioPanel.querySelector('.similar-container').appendChild(newEl);
                    }
                }
            });
        }
        // if (query.studio) {
        //     console.log('Making performer panel');
        //     makeApiRequestGET('get-similar-performers', [query.actor], performers => {
        //         if (performers) {
        //             console.log('performers:', performers);
        //             const modelStudioPanel = document.getElementById('model-studio-panel');
        //             modelStudioPanel.style.display = 'flex';
        //             modelStudioPanel.querySelector('.focus-performer').innerText = query.actor;
        //             for (let i = 1; i < 9; i++) {
        //             // for (let perf_data of performers) {
        //                 const perf_data = performers[i];
        //                 const newEl = document.createElement('a');
        //                 newEl.href = 'searchPage.html?' + (new URLSearchParams({'performer': perf_data.name})).toString();
        //                 newEl.innerText = perf_data.name;
        //                 modelStudioPanel.querySelector('.similar-container').appendChild(newEl);
        //             }
        //         }
        //     });
        // }
    });
}



