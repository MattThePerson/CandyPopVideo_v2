import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET, makeApiRequestPOST_JSON } from '../../shared/util/request.js';
import { render_video_cards } from '../../shared/util/load.js';
import { configure_page_nav } from './page_nav.js';


injectComponents();


/* NEEDS REFACTORING FROM HERE */

const searchPanel = document.getElementById('search-panel');
const searchButton = document.getElementById('search-button');
/** @type {HTMLInputElement} */
const onlyFavsCheckbox = document.querySelector('input.only_favourites');

const urlParams = new URLSearchParams(window.location.search);


//region - FUNCTION ----------------------------------------------------------------------------------------------------


/**
 * @param {HTMLElement} searchPanel
 */
function initiate_search(searchPanel) {
    let params = new URLSearchParams();
    const urlparams_sortby = urlParams.get('sortby');
    if (urlparams_sortby) {
        params.set('sortby', urlparams_sortby);
    }

    /* get query data from query elements inputs */
    searchPanel.querySelectorAll('.search-element').forEach(el => {
        const a = Array.from(el.classList).find(cls => cls !== 'search-element') || null;
        if (a === null) {
            console.error('.search-element has no additional class');
        } else {
            const key = a.replace('-input', '');
            const value = el.querySelector('input').value;
            if (value !== '') {
                params.set(key, value);
            }
        }
    });
    if (onlyFavsCheckbox.checked) {
        params.set('only_favourites', 'true');
    }
    if (params.size > 0) {
        window.location.href = window.location.pathname + '?' + params.toString();
    } else {
        console.log("No search parameters given")
    }
}

function get_search_page_title(urlParams) {
    let arr = [];
    for (let param of ['query', 'actor', 'studio', 'collection']) {
        if (urlParams.get(param)) {
            arr.push(urlParams.get(param));
        }
    }

    return arr.join(', ') + ' SEARCH RESULTS';
}


function highlight_sort_button(sortBy) {
    if (sortBy.includes('random')) {
        sortBy = sortBy.split('-')[0];
    }
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


function make_performer_panel() {
    console.log('Making performer panel');
    makeApiRequestGET('/api/query/get/similar-actors', [query.actor], (actors) => {
        if (actors) {
            console.log('similar actors:', actors);
            const modelStudioPanel = document.getElementById('model-studio-panel');
            modelStudioPanel.style.display = 'flex';
            $('.focus-performer').text(query.actor);
            for (let i = 1; i < 12; i++) {
            // for (let perf_data of performers) {
                const actor_data = actors[i];
                const newEl = document.createElement('a');
                newEl.href = '/pages/search/page.html?' + (new URLSearchParams({'performer': actor_data.name})).toString();
                newEl.innerText = actor_data.name;
                modelStudioPanel.querySelector('.similar-container').appendChild(newEl);
            }
        }
    });
}




//region - EVENT LISTENERS ---------------------------------------------------------------------------------------------

searchButton.addEventListener('click', arg => {
    initiate_search(searchPanel);
});

document.querySelectorAll('#search-panel .search-input').forEach(inputElement => {
    inputElement.addEventListener('keydown', (/** @type {KeyboardEvent} */ event) => {
        if (event.key === 'Enter') {
            initiate_search(searchPanel);
        }
    });
});


// update sortby buttons
/** @type {*} */
const button_groups = searchPanel.querySelectorAll('.sort-panel .button-group');
for (let button_group of button_groups) {
    let sort_type = button_group.id.replace('-button-group', '');
    let main = button_group.querySelector('.main');
    let asc = button_group.querySelector('.asc');
    let desc = button_group.querySelector('.desc');
    main.addEventListener('click', e => {
        let sort_by_arg = null;
        if (sort_type == 'random') {
            const random_seed = Math.floor(Math.random() * 9999) + 1;;
            sort_by_arg = `random-${random_seed}`;
        } else {
            if (main.classList.contains('selected')) {
                if (desc.classList.contains('selected'))
                    sort_by_arg = sort_type + '-asc';
                else
                    sort_by_arg = sort_type + '-desc';
            } else {
                sort_by_arg = sort_type + '-desc';
                if (sort_type == 'filename' || sort_type == 'scene-title' || sort_type == 'studio')
                    sort_by_arg = sort_by_arg.replace('desc', 'asc');
            }
        }
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('sortby', sort_by_arg);
        urlParams.delete('page');
        window.location.href = window.location.pathname + '?' + urlParams.toString();
    });
    if (sort_type != 'random') {
        asc.addEventListener('click', e => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('sortby', sort_type + '-asc');
            urlParams.delete('page');
            window.location.href = window.location.pathname + '?' + urlParams.toString();
        });
        desc.addEventListener('click', e => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('sortby', sort_type + '-desc');
            urlParams.delete('page');
            window.location.href = window.location.pathname + '?' + urlParams.toString();
        });
    }
}


//endregion

//region - QUERY -------------------------------------------------------------------------------------------------------


const params = new URLSearchParams(window.location.search);
const results_per_page = 24;

/* make page changes */

document.title = get_search_page_title(params);

params.forEach((value, key) => {
    try {
        const selector = `.${key}-input input`;
        $(selector).val(params.get(key));
    } catch {
        console.log('No such element: ', `.${key}-input input`);
    }
});


/* add page number */
const pageNumber = parseInt(params.get('page')) || 1;
// document.querySelector('#search-page-info .page-number').innerText = 'Page ' + pageNumber;
$('#search-page-info .page-number').text('Page ' + pageNumber)


/* construct query */
const query = {
    search_string: null,    // str,
    actor: null,            // str,
    studio: null,           // str,
    collection: null,       // str,
    include_terms: null,      // list[str],
    exclude_terms: null,      // list[str],
    date_added_from: null,      // str,
    date_added_to: null,        // str,
    date_released_from: null,   // str,
    date_released_to: null,     // str,
    only_favourites: false,     // bool,
    sortby: null,               // str|None,
    limit: null,                  // int,
    startfrom: -1,              // int,
}


/* url params to query */
params.forEach((value, key) => {
    if (key in query) {
        query[key] = value;
    }
});

query.limit =       params.get('results-amount') || results_per_page;
query.startfrom =   query.limit * (pageNumber-1);

if (typeof query.include_terms === 'string') query.include_terms = query.include_terms.split(',').map(w => w.trim());
if (typeof query.exclude_terms === 'string') query.exclude_terms = query.exclude_terms.split(',').map(w => w.trim());

if (query.include_terms === null)  query.include_terms = [];
if (query.exclude_terms === null)  query.exclude_terms = [];

console.log('Query: ', query)

/* make ui changes based on params (using query) */
if (query.sortby) highlight_sort_button(query.sortby);
else              highlight_sort_button('date-added-desc');

if (query.only_favourites)  onlyFavsCheckbox.checked = true;


//region - BACKEND REQUEST ---------------------------------------------------------------------------------------------

if (urlParams.size > 0) {
    makeApiRequestPOST_JSON('/api/query/search-videos', query, (results) => {
        
        console.log('search_results:', results);
        // return;

        const card_type = "search-result-card-default"; // TODO: Replace with local storage
        
        const results_container = $('.similar-videos-section').get(0);
        
        // generate_results(results, results_container);

        render_video_cards(
            results.search_results,
            results_container,
            results_per_page,
        )

        /* Configure page nav */
        configure_page_nav(results.videos_filtered_count, results.time_taken, results_per_page, query.startfrom);
        
        /* similar performers */
        if (query.actor) {
            make_performer_panel();
        }

    });
}



