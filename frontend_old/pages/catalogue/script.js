
import { injectComponents } from '../../shared/util/component.js'
injectComponents();


// #region - MAIN ------------------------------------------------------------------------------------------------------

async function main() {

    /* Ensure catalogue type in url */
    const default_type = 'actor';
    const default_sortby = 'newest-video';

    
    /* REQUEST CATALOGUE */
    const query = {
        query_type: 'actors',        //  str = [ actors | studios ]
        query_string: null,          //  str|None
        use_primary_actors: true,    //  bool
        filter_actor: null,          //  str|None
        filter_studio: null,         //  str|None
        filter_collection: null,     //  str|None
        filter_tag: null,            //  str|None
    }
    console.debug("QUERY:", query);
    
    const response = await $.ajax({
        url: '/api/query/get/catalogue',
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(query),
    });

    console.debug('CATALOGUE:', response);

    const catalogue_nav_buttons = $('.catalogue-page-nav button')
    const sortby_buttons = $('.sortby-options-bar button');
    
    /* RENDER CATALOGUE */
    const renderCatalogue = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const catalogue_type = urlParams.get('type') || default_type;
        const catalogue_sortby = urlParams.get('sortby') || default_sortby;
        const scene_count_thresh = $('.count-thresh-slider').val();

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

    /* count thresh inputs */
    const count_thresh_slider = $('.count-thresh-slider');
    const count_thresh_input = $('.count-thresh-input');
    count_thresh_slider.on('input', () => {
        count_thresh_input.val(count_thresh_slider.val());
    });
    count_thresh_slider.on('change', () => {
        renderCatalogue();
    });

    count_thresh_input.on('keydown', () => {
        count_thresh_slider.val(count_thresh_input.val());
        renderCatalogue();
    })
    
    
    
    
    
}


// #endregion

// #region - METHODS ---------------------------------------------------------------------------------------------------

function renderCatalogueList(catalogue, type, sortby, count_thresh) {

    const key = type + '_info';
    const items = catalogue[key].filter(item => item.VideoCount >= count_thresh);
    // console.log(key, items);
    const list_container = $('.catalogue-list');
    list_container.html('');
    $('.item-count-display').text(`${items.length} ${type}s with at least ${count_thresh} videos`);
    
    if (items.length === 0) return;

    const letter_nav = $('.letter-nav');
    letter_nav.hide();
    
    switch (sortby) {
        case "alphabetic":
            items.sort((a, b) => a.Name.localeCompare(b.Name));
            renderCatalogueList_alphabetic(items, list_container, type, letter_nav);
            break;
        case "count":
            items.sort((a, b) => b.VideoCount - a.VideoCount);
            renderCatalogueList_count(items, list_container, type);
            break;
        case "newest-video":
            items.sort((a, b) => b.NewestVideo.localeCompare(a.NewestVideo));
            renderCatalogueList_count(items, list_container, type)
            break;
    }
    
}

function renderCatalogueList_alphabetic(items, container, type, letter_nav) {

    letter_nav.html('');
    letter_nav.css('display', 'flex');

    console.log(items);
    
    // const null_item = 'NULL_ITEM_12323434';
    let current_letter = null;
    let group = [];
    for (let i = 0; i <= items.length; i++) {
        let first_letter, item;
        if (i !== items.length) {
            item = items[i];
            first_letter = item.Name[0];
            if (!current_letter) {
                current_letter = first_letter;
            }
        }
        
        if (i !== items.length && current_letter == first_letter) {
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
    for (let item of items) {
        inner_html += get_item_span(
            item.Name,
            item.VideoCount,
            item.NewestVideo,
            item.NewVideoCount,
            type,
        );
    }
    container.append(/* html */`
        <div class="item-group">
            ${inner_html}
        </div>
    `)
    
}

function renderCatalogueList_newestVideo(items, container, type) {
    
    let inner_html = '';
    for (let item of items) {
        inner_html += get_item_span(
            item.Name,
            item.VideoCount,
            item.NewestVideo,
            item.NewVideoCount,
            type,
        );
    }
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
                        top: el.getBoundingClientRect().top + window.scrollY - 190,
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

    for (let item of items) {
        inner_html += get_item_span(
            item.Name,
            item.VideoCount,
            item.NewestVideo,
            item.NewVideoCount,
            type,
        );
    }
    
    return /* html */`
        <div class="alphabetic-group group-${letter.toUpperCase()}">
            <h2>${letter.toUpperCase()}</h2>
            <div class="item-group">
                ${inner_html}
            </div>
        </div>
    `;
}

function get_item_span(name, count, newest, new_vids, type) {
    const newest_ago = _format_date_added(newest);
    return /* html */`
        <div class="item-span">
            <div title="videos added in last 7 days" class="new-vids">
                ${(new_vids) ? new_vids + " new" : ""}
            </div>
            <a class="item-link" href="/pages/search/page.html?${type}=${name}">
                <div class="name-container">
                    <div class="name">${titleCase(name)}</div>
                    <div class="separator"></div>
                    <div class="count">${count} vids</div>
                </div>
            </a>
            <div class="newest-container">
                <div title="newest video added: ${newest}" class="newest">updated ${newest_ago} ago</div>
            </div>
        </div>
    `
}


// #endregion

// #region - HELPERS ---------------------------------------------------------------------------------------------------

const titleCase = str =>
    str.replace(/\b\w/g, char => char.toUpperCase());


function _format_date_added(date_added) {
    let diff_ms = (new Date()).getTime() - (new Date(date_added.replace(' ', 'T'))).getTime();
    let string = ['sec', 'min', 'hour', 'day', 'week', 'month', 'year', 'decade', 'century', 'millenia'];
    let mult =  [60, 60, 24, 7, 4.345, 12, 10, 10, 10];
    let limit = [60, 60, 24, 7, 3*4.345, 12*3, 10, 10, 10, 10];
    let ms = 1000;
    for (let i = 0; i < mult.length; i++) {
        if (diff_ms < ms*limit[i]) {
            let unit = Math.floor(diff_ms / ms);
            let ret = unit + ' ' + string[i];
            if (unit > 1)
                ret = ret + 's';
            return ret;
        }
        ms *= mult[i];
    }
}


// #endregion


main();

