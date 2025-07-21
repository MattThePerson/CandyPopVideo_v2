
import { injectComponents } from '../../shared/util/component.js'
injectComponents();


// #region - MAIN ------------------------------------------------------------------------------------------------------

async function main() {

    /* Ensure catalogue type in url */
    const default_type = 'actor';
    const default_sortby = 'alphabetic';
    // const urlParams = new URLSearchParams(window.location.search);

    // if (!urlParams.has('type')) {
    //     urlParams.set('type', default_type);
    //     const new_url = window.location.href + '?' + urlParams.toString();
    //     history.pushState(null, '', new_url);
    // }

    
    /* REQUEST CATALOGUE */
    const query = {
        query_type: 'actors',        //  str = [ actors | studios ]
        query_string: null,          //  str|None
        use_primary_actors: true,    //  bool
        filter_performer: null,      //  str|None
        filter_studio: null,         //  str|None
        filter_collection: null,     //  str|None
        filter_tag: null,            //  str|None
    }
    
    const response = await $.ajax({
        url: '/api/query/get/catalogue',
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(query),
    });

    // console.log('catalogue:', response);

    const catalogue_nav_buttons = $('.catalogue-page-nav button')
    const sortby_buttons = $('.sortby-options-bar button');
    
    const renderCatalogue = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const catalogue_type = urlParams.get('type') || default_type;
        const catalogue_sortby = urlParams.get('sortby') || default_sortby;
        const scene_count_thresh = 10;

        /* page changes */
        catalogue_nav_buttons.each((_, button) => button.classList.remove('selected') );
        sortby_buttons.each((_, button) => button.classList.remove('selected'));
        $('#nav-button-' + catalogue_type).addClass('selected');
        $('#sortby-button-' + catalogue_sortby).addClass('selected');
        document.title = document.title + ': ' + catalogue_type;

        /* render list */
        renderCatalogueList(response, catalogue_type, catalogue_sortby, scene_count_thresh)

    }


    renderCatalogue();
    
    /* EVENT LISTENERS */

    catalogue_nav_buttons.each((_, button) => {
        $(button).on('click', () => {
            if (!$(button).hasClass('selected')) {
                window.scrollTo(0, 0);
                const type = button.id.replace('nav-button-', '');
                const params = new URLSearchParams(window.location.search);
                params.set('type', type);
                const new_url = window.location.origin + window.location.pathname + '?' + params.toString();
                history.pushState(null, '', new_url);
                renderCatalogue();
            }
        });
    })

    sortby_buttons.each((_, button) => {
        $(button).on('click', () => {
            if (!$(button).hasClass('selected')) {
                window.scrollTo(0, 0);
                const sortby = button.id.replace('sortby-button-', '');
                const params = new URLSearchParams(window.location.search);
                params.set('sortby', sortby);
                const new_url = window.location.origin + window.location.pathname + '?' + params.toString();
                history.pushState(null, '', new_url);
                renderCatalogue();
            }
        })
    });

    window.addEventListener('popstate', renderCatalogue);
    
}


// #endregion

// #region - METHODS ---------------------------------------------------------------------------------------------------

function renderCatalogueList(catalogue, type, sortby, count_thresh) {

    const key = type + '_counts';
    const items = catalogue[key].filter(item => item[1] >= count_thresh);
    const list_container = $('.catalogue-list');
    list_container.html('');
    
    if (items.length === 0) return;
    
    if (sortby === 'alphabetic') {
        items.sort();
        renderCatalogueList_alphabetic(items, list_container, type);
    } else if (sortby === 'count') {
        renderCatalogueList_count(items, list_container, type);
    }
    
}

function renderCatalogueList_alphabetic(items, container, type) {

    const letter_nav = $('.letter-nav');
    letter_nav.html('');
    letter_nav.css('display', 'flex');
    
    const null_item = 'NULL_ITEM_12323434';
    let current_letter = null;
    let group = [];
    for (let i = 0; i <= items.length; i++) {
        const item = items[i] || null_item;
        const first_letter = item[0][0];
        if (!current_letter) {
            current_letter = first_letter;
        }
        
        if (item !== null_item && current_letter == first_letter) {
            group.push(item);
        } else  { // render group
            if (group.length > 0) {
                container.append(  get_alphabetic_group_html(current_letter, group, type) );
                letter_nav.append( get_letter_nav_button(current_letter.toUpperCase()) );
            }
            group = [item];
            current_letter = first_letter;
        }
    }
    
}

function renderCatalogueList_count(items, container, type) {
    
    let inner_html = '';
    for (let [name, count] of items) {
        inner_html += get_item_span(name, count, type);
    }
    // padding: 0 1rem 0.5rem 1rem;
    // margin-left: 1rem;
    container.append(/* html */`
        <div class="item-group">
            ${inner_html}
        </div>
    `)
    
}

/* OTHER */

function get_letter_nav_button(letter) {
    return $('<button></button>')
            .text(letter)
            .on('click', () => {
                $('.alph-group-highlighted').removeClass('alph-group-highlighted');
                const el = $('.alphabetic-group.group-'+letter).get(0)
                el.classList.add('alph-group-highlighted');
                window.scrollTo({
                        top: el.getBoundingClientRect().top + window.scrollY - 170,
                        behavior: 'smooth',
                    })
                document.addEventListener('wheel', () => {
                    console.log('scroll'),
                    $('.alph-group-highlighted').removeClass('alph-group-highlighted');
                }, {once: true});
            });
}


function get_alphabetic_group_html(letter, items, type) {

    let inner_html = '';

    for (let [name, count] of items) {
        inner_html += get_item_span(name, count, type);
    }
    
    return /* html */`
        <div class="alphabetic-group group-${letter.toUpperCase()}">
            <h2>${letter.toUpperCase()}</h2>
            ${inner_html}
        </div>
    `;
}

function get_item_span(name, count, type) {
    return /* html */`
        <a class="item-span" href="/pages/search/page.html?${type}=${name}">
            <div class="name">${titleCase(name)}</div>
            <div class="separator"></div>
            <div class="count">${count}</div>
        </a>
    `
}


const titleCase = str =>
    str.replace(/\b\w/g, char => char.toUpperCase());


// #endregion


main();

