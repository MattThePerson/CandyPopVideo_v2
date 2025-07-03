

import { makeApiRequestGET } from "./request.js";


//region - MAIN --------------------------------------------------------------------------------------------------------

export function generate_results(results, args, query) {

    // console.log('generating results:', results)
    
    render_wordcloud(results.word_cloud);

    const videoResultsContainer = document.getElementById('video-results-container');
    const videoResultTemplate = document.getElementById('video-result-template');
    let posters_loaded = 0;

    /* ensure posters and teasers for search results */
    results.search_results.forEach( (result, idx) => {
        let resultItem = make_search_result_item(result, videoResultTemplate);
        videoResultsContainer.appendChild(resultItem);
        
        const img_el = document.querySelector(`#item-${result.hash} .thumbnail`);
        img_el.src = '/media/get/poster/' + result.hash + '?t=' + Date.now();  // add time to force cache busting
        img_el.onload = () => {
            posters_loaded++;
            if (posters_loaded === results.search_results.length) {
                // console.log('Loading small teasers');
                _ensure_search_results_small_teasers(results.search_results);
            }
        }
    });
    
    // Add event listener to search results to play teasers
    if (document.getElementById('video-results-container').classList.contains('default-view')) {
        document.querySelectorAll('.video-result-item .thumb-container').forEach(item => {
            const video = item.querySelector('.thumb-container video');
            const image = item.querySelector('.thumb-container .thumbnail');
            const spinner = item.querySelector('.spinner');
            item.addEventListener('mouseenter', () => {
                image.style.display = 'none';
                if (video.src == '') {
                    spinner.style.display = 'block';
                } else {
                    video.style.display = 'block';
                    if (video.paused) {
                        video.play();
                    }
                }
            });
            item.addEventListener('mouseleave', () => {
                video.style.display = 'none';
                image.style.display = 'block';
                video.pause();
                // video.currentTime = 0;
                spinner.style.display = 'none';
            });
        });
    }

    // Configure page nav
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


//region - MAIN HELPERS ------------------------------------------------------------------------------------------------


/* 4 uses */
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


function format_added_time(date_added) {
    let diff_ms = (new Date()) - (new Date(date_added.replace(' ', 'T')));
    let string = ['second', 'minute', 'hour', 'day', 'week', 'month', 'year'];
    let mult =  [60, 60, 24, 7, 4.345, 12, 10];
    let limit = [60, 60, 24, 7, 3*4.345, 12*3, 10];
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


function make_search_result_item(res, videoResultTemplate) {
    const template = videoResultTemplate.content.cloneNode(true);
    const item = template.querySelector('.video-result-item');
    item.id = 'item-' + res.hash;
    item.setAttribute('data-hash', res.hash);
    let duration = res.duration;
    if (duration.startsWith("0:")) {
        duration = duration.substring(2);
    }
    if (res.scene_title)  {
        let mention_performers = '';
        // if (res.mention_performer)
        //     mention_performers = ' (' + res.mention_performer + ')'
        let line_str = '';
        if (res.line)
            line_str = '[' + res.line + '] '
        let jav_code_str = '';
        if (res.jav_code)
            jav_code_str = '[' + res.jav_code + '] '
        template.querySelector('h2').innerText = jav_code_str + line_str + res.scene_title;
    } else {
        template.querySelector('h2').innerText = res.filename;
    }
    template.querySelector('.resolution').innerText = res.resolution + 'p';
    template.querySelector('.resolution').style.color = getResolutionTextColor(res.resolution);
    try {
        template.querySelector('.duration').innerText = duration;
    } catch {}
    try {
        template.querySelector('.duration-pretty').innerText = formatDuration(duration);
    } catch {}
    if (res.fps == 29) res.fps = 30;
    template.querySelector('.fps').innerText = res.fps + 'fps';
    template.querySelector('.bitrate').innerText = Math.round(res.bitrate/100)/10 + 'mb';
    template.querySelector('.bitrate').style.color = getBitrateTextColor(res.bitrate);
    const actor_container = template.querySelector('.actors');
    let performers = res.performers;
    // if (res.mention_performer) {
    //     for (let perf of res.mention_performer.split(', ')) {
    //         performers.push(perf);
    //     }
    // }
    for (let performer of performers) {
        let span = document.createElement('span');
        let el = document.createElement('a');
        el.classList.add('actor');
        el.innerText = performer;
        el.href = '/pages/search/page.html?' + String(new URLSearchParams({'performer' : performer}));
        el.addEventListener('dragstart', event => event.dataTransfer.setData('text/plain', performer)); // add dragging the performer name
        span.appendChild(el);
        actor_container.appendChild(span);
    }
    if (res.studio) {
        template.querySelector('.studio').innerText = res.studio;
        template.querySelector('.studio').href = '/pages/search/page.html?' + String(new URLSearchParams({'studio' : res.studio}));
        template.querySelector('.studio').addEventListener('dragstart', event => event.dataTransfer.setData('text/plain', res.studio)); // add dragging the performer name
    } else {
        template.querySelector('.studio').style.display = 'none';
    }
    try {
        if (res.line && template.querySelector('.line')) {
            template.querySelector('.line').innerText = res.line;
            template.querySelector('.line').href = '/pages/search/page.html?' + String(new URLSearchParams({'include-terms' : res.line}));
            template.querySelector('.line').addEventListener('dragstart', event => event.dataTransfer.setData('text/plain', res.line));
        } else {
            template.querySelector('.line').parentNode.style.display = 'none';
        }
    } catch {}

    template.querySelector('.year').innerText = res.date_released_d18 || res.date_released || res.year || '';
    template.querySelector('.collection').innerText = res.collection;
    if (res.collection == '') {
        template.querySelector('.collection').style.display = 'none';
    }
    template.querySelector('.lower-bar .added-tag').innerText = 'Added ' + format_added_time(res.date_added) + ' ago';
    let descriptionEl = template.querySelector('p.description');
    if (descriptionEl && res.scene_description) {
        descriptionEl.innerText = res.scene_description
    }

    // TAGS
    const tags_container = template.querySelector('.tags-bar');
    for (let tag of res.tags) {
        let el = document.createElement('div');
        el.classList.add('tag');
        el.innerText = tag;
        tags_container.appendChild(el);
    }
    if (res.jav_code) {
        template.querySelector('h2').innerText = res.jav_code;
        if (descriptionEl && 'title' in res) {
            descriptionEl.innerText = res.title;
        }
    }
    template.querySelectorAll('.video-result-item > a').forEach(el => {
        el.href = '/pages/video/page.html?hash=' + res.hash;
        el.addEventListener('dragstart', event => event.dataTransfer.setData('text/plain', res.filename)); // add draggin the performer name
    });

    // make favourite indicator visible
    makeApiRequestGET('/api/interact/favourites/check', [res.hash], response => {
        if (response.is_favourite) {
            const resItem = document.querySelector('#item-' + res.hash);
            try {
                resItem.querySelector('.favourite').style.display = 'block';
            } catch {}
        }
    });

    return template;

}


// recursively loads an array of videos sequentially
function _ensure_search_results_small_teasers(search_results, idx=0) {

    if (idx == search_results.length) {
        return;
    }
    
    let current = search_results[idx];
    // console.log('idx:', idx, search_results.length);

    makeApiRequestGET('/media/ensure/teaser-small', [current.hash], () => {
        const video_el = document.querySelector('#item-' + current.hash + ' video');
        video_el.preload = 'auto';
        video_el.src = `/static/preview-media/0x${current.hash}/teaser_small.mp4`;
        video_el.addEventListener('canplay', () => {
            // put it here to only load next when previous can play
        });
        _ensure_search_results_small_teasers(search_results, idx+1);
    });

}


/* render wordcloud */
function render_wordcloud(words) {
    let limit = 35;
    const canvas = document.getElementById('wordCloudCanvas');
    if (!canvas) {
        return;
    }
    // const maxFreq = Math.sqrt(Math.max(...words.map(([, freq]) => freq)));
    const totalFreq = Math.sqrt( words.reduce((sum, item) => sum + item[1], 0) );
    const wordArray = words.slice(0, limit).map(([word, freq]) => 
        [ word, Math.sqrt(freq) / totalFreq * 40 ]
    );
    const urlParams = '...';
    const config = {
        list: wordArray,
        gridSize: 20,
        weightFactor: 7,
        fontFamily: 'Times, serif',
        color: '#ddd',
        backgroundColor: '#222',
        drawOutOfBound: false,
        rotateRatio: 0,
        rotationSteps: 2,
        hover: function(item) {
            if (item) {
            canvas.style.cursor = 'pointer';
            } else {
            canvas.style.cursor = 'default';
            }
        },
        click: function(item) {
            let ic = urlParams.get('include_terms');
            if (ic) {
                ic += ', ' + item[0];
            } else {
                ic = item[0]
            }
            urlParams.set('include_terms', ic)
            window.location.href = 'pages/search/page.html?' + urlParams.toString();
        }
    };
    WordCloud(canvas, config);
}


//region - MISC. HELPERS -----------------------------------------------------------------------------------------------


function formatDuration(duration) {
    const parts = duration.split(':');
    let hours = 0, minutes = 0, seconds = 0;
    if (parts.length === 2) {
        [minutes, seconds] = parts;
    } else if (parts.length === 3) {
        [hours, minutes, seconds] = parts;
    } else {
        return "Invalid format";
    }
    const partsArray = [];
    if (hours) partsArray.push(`${hours}h`);
    partsArray.push(`${minutes}m`);
    partsArray.push(`${seconds}s`);
    return partsArray.join(" ");
}

function getResolutionTextColor(res) {
    return 'white';
    if (res >= 2160)
        return '#ffe521';
    else if (res >= 1440)
        return '#24fc03';
    else if (res >= 1080)
        return '#03fcd7';
    /* else if (res >= 720)
        return '#647afa' */
    return 'white';
}

function getBitrateTextColor(br) {
    return 'white';
    const colors = {
        1 : 'red',
        2 : 'pink',
        3 : 'green',
        5 : 'blue',
        7 : 'purple',
        10 : 'gray',
        15 : 'cyan'
    }
    for (let [n, color] of Object.entries(colors)) {
        if (br/1000 < n) 
            return color;
    }
    return 'yellow'
}

