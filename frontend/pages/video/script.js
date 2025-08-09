import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js';
import { load_video_player } from './player_old.js';
import { load_recommended_videos } from './recommended_videos.js';
import { get_actor_card } from './components.js';

injectComponents();


// #region - MAIN ------------------------------------------------------------------------------------------------------

function main(video_hash) {

    /* - video data --------------------------------------------------------- */

    makeApiRequestGET('/api/get/video-data', [video_hash], async (video_data) => {
        console.debug('VIDEO DATA:', video_data);
        
        document.title = get_video_page_title(video_data);
        
        /* load video player */
        load_video_player(video_hash, video_data, urlParams);
    
        /* Hydrate video about section */
        const info_section = $('section.video-info-section');
        hydrate_info_section(info_section, video_data);
    
        return;
        
        /* load recommended (related & similar) videos */
        const related_videos_section = $('section.related-videos-section').get(0);
        const similar_videos_section = $('.similar-videos-section').get(0);
        load_recommended_videos(
            video_data,
            related_videos_section,
            similar_videos_section,
        );
        
    });
    
    // return;
    
    /* - video interactions ------------------------------------------------- */

    makeApiRequestGET('/api/interact/get', [video_hash], vi => {

        console.debug('INTERACTIONS:', vi);
        
        /* info section */
        $(".viewtime td").text(_format_seconds(vi.viewtime));
        if (vi.last_viewed) {
            const lv = vi.last_viewed.replace("T", " ").split(".")[0];
            $(".last-viewed td").text(`${lv} (${_format_date_added(lv)} ago)`);
        }
        
        /* likes */
        const likes_button = $('.like-button');
        likes_button.find("span").text(`${vi.likes} likes`);
        likes_button.on('click', () => {
            console.debug("Adding ❤️");
            $.post('/api/interact/likes/add/'+video_hash, (data, status) => {
                if (status === 'success') {
                    likes_button.find("span").text(`${++vi.likes} likes`);
                    likes_button.addClass("liked");
                }
            })
        })

        /* date markers */
        const date_marker_button = $('.add-dated-marker');
        date_marker_button.on('click', () => {
            // ...
        });
        
        /* favourited date */
        if (vi.is_favourite) {
            setupFavouritedDate(video_hash, vi)
        }

    });

}

// #endregion

// #region - METHODS ---------------------------------------------------------------------------------------------------


/**
 * 
 * @param {JQuery<HTMLElement>} section 
 * @param {Object} vd 
 */
function hydrate_info_section(section, vd) {
    
    /* quick stats section */
    section.find('.duration').text(_format_seconds(vd.duration_seconds));
    section.find('.resolution').text(vd.resolution + 'p');
    section.find('.fps').text(vd.fps + 'fps');
    section.find('.bitrate').text(Math.floor(vd.bitrate/100)/10 + ' MB/s');
    section.find('.filesize').text(_format_filesize(vd.filesize_mb));

    /* video info (right side) */
    const da = vd.date_added.replace("T", " ");
    $(".date-added td").text(`${da.slice(0,-6)} (${_format_date_added(da)} ago)`);
    const [ parent, name ] = getParentDirAndName(vd.path);
    $(".filename td").text(name);
    // $(".filename td").attr("title", name);
    $(".parent-directory td").text(parent);
    $(".parent-directory td").attr("title", parent);
    
    /* title/year */
    let title_fmt = vd.title.replace(';', ':');
    if (vd.dvd_code) title_fmt = `[${vd.dvd_code}] ` + title_fmt;
    section.find('.title-bar h1').text( title_fmt );
    section.find('.year').text( vd.date_released );

    section.find('.collection').text( vd.collection );
    section.find('.collection').attr('href', `/pages/search/page.html?collection=${vd.collection}`)

    /* add studios */
    const studios_cont = section.find('.studios-container');
    [vd.studio, vd.line].forEach((studio, idx) => {
        if (studio) {
            if (idx !== 0) studios_cont.append(`<div></div>`);
            const el = document.createElement('a');
            el.href = '/pages/search/page.html?studio=' + studio;
            el.innerText = studio;
            studios_cont.append(el);
            $.get('/api/get/studio-video-count/' + studio, (data, status) => {
                if (status === "success") {
                    el.innerText += ` (${data.video_count} vids)`
                }
            })
        }
    })
    
    /* add actors */
    let video_dr = vd.date_released;
    if (video_dr && video_dr.length == 4) video_dr = video_dr + '-06-01';
    const actors_cont = section.find('.actors-container');
    vd.actors.forEach((actor) => {
        const [actor_card, callback] = get_actor_card(actor);
        actors_cont.append(actor_card);
        $.get('/api/get/actor/'+actor, (data, status) => {
            console.debug('ACTOR DATA:', actor, data);
            if (status === 'success') {
                const age_its = get_year_difference_between_dates(data.date_of_birth, video_dr);
                let pp;
                try {
                    const pp_rel = data.galleries[0];
                    pp = '/static/actor-store' + pp_rel;
                } catch {}

                callback({
                    video_count: null, // TODO: figure out faster way to get video count at this point
                    age_its: age_its || null,
                    profile_pic: pp,
                    aka: data.aka ? data.aka.join(', ') : null,
                });
            }
        });
    });

    /* add tags */
    let html = '';
    vd.tags.forEach(tg => {
        html += /* html */ `
            <a href="/pages/search/page.html?tags=${tg}">
                ${tg}
            </a>
        `
    })
    $(".tags-bar").html(html);

    if (vd.description && vd.description !== "") {
        $(".description").show();
        $(".description p").text(vd.description);
    }

    /* EVENT LISTENERS */

    /* check favourite */
    const is_fav_button = section.find('button.is-fav-button');
    $.get(`/api/interact/favourites/check/${vd.hash}`, (is_favourite, status) => {
        if (status === 'success') {
            console.log("is_favourite:", is_favourite);
            is_fav_button.addClass('loaded');
            if (is_favourite) {
                is_fav_button.addClass('is-fav');
            }
            // add event listeners
            is_fav_button.on('click', () => {
                let change_favourite_route;
                if (is_fav_button.hasClass('is-fav')) {
                    change_favourite_route = `/api/interact/favourites/remove/${vd.hash}`;
                } else {
                    change_favourite_route = `/api/interact/favourites/add/${vd.hash}`;
                }
                $.post(change_favourite_route, (data, status) => {
                    if (status === 'success') {
                        is_fav_button.toggleClass('is-fav');
                    }
                });
            });
        }
    });
    

}



function setupFavouritedDate(video_hash, vi) {
    
    const input = $(".favourited-date td input");
    let fav_dt = vi.favourited_date.replace("T", " ");
    $(".favourited-date").show()
    input.val(fav_dt);
    $(".favourited-date td span").text(`(${_format_date_added(fav_dt)} ago)`)
    
    /* event listener */
    input.on("keydown", e => {
        if (e.key === "Enter") {
            input[0].blur()
            const new_fav_dt = (input.val()).toString();

            console.debug("NEW DATE: ", new Date(new_fav_dt))
            const valid_date = !isNaN((new Date(new_fav_dt)).getTime())
            if (!valid_date) {
                // input.val(fav_dt);
                input.css("background", "#d229");
                setTimeout(() => input.css("background", "none"), 1500);
                return
            }
            
            /* post new date */
            console.debug("Sending new favourited date:", new_fav_dt)
            $.post(`/api/interact/favourites/update-time/${video_hash}/${new_fav_dt}`)
                .done((data, status, xhr) => {
                    console.log('Success:', data);
                    fav_dt = new_fav_dt;
                    $(".favourited-date td span").text(`(${_format_date_added(fav_dt)} ago)`)
                    input.css("background", "#2e39");
                    setTimeout(() => input.css("background", "none"), 1500);
                })
                .fail((xhr) => {
                    // console.log('Error status:', xhr.status);
                    console.log('Error message:', xhr.responseText);
                    // input.val(fav_dt);
                    input.css("background", "#e719");
                    setTimeout(() => input.css("background", "none"), 1500);
            });

        }
    })
}


function get_video_page_title(video_data)  {
    let title = video_data.primary_actors.join(', ');
    if (video_data.studio) {
        title += ` - ${video_data.studio}`;
    }
    title += ` - ${video_data.title}`;
    return title;
}



function get_year_difference_between_dates(date1, date2) {
    if (!date1 || !date2) {
        return null;
    }
    if (date1.length < 4 || date2.length < 4) {
        return null;
    }
    const a = Date.parse(date1);
    const b = Date.parse(date2);
    if (isNaN(a) || isNaN(b)) {
        return null;
    }
    let year_diff = Math.floor((b-a) / (1000 * 60 * 60 * 24 * 365));
    return Math.max(year_diff, 18);
}


// #endregion

// #region - HELPERS ---------------------------------------------------------------------------------------------------

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function _format_seconds(seconds) {

    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor( (seconds-hours*3600) / 60 );
    const secs = Math.floor( seconds - hours*3600 - mins*60 );

    if (hours > 0) {
        return `${hours}h ${mins}m ${secs}s`;
    } else if (mins > 0) {
        return `${mins}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
    
}

function _format_date_added(date_added) {
    let diff_ms = (new Date()).getTime() - (new Date(date_added.replace(' ', 'T'))).getTime();
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


function _format_filesize(mb) {
    if (mb >= 1000) {
        return (Math.floor(mb/100)/10).toString() + ' GB';
    }
    return (Math.floor(mb)).toString() + ' MB';
}

function getParentDirAndName(absPath) {
    const norm = absPath.replace(/\\/g, '/'); // normalize Windows to /
    const parts = norm.split('/');
    const name = parts.pop();
    const parent = parts.join('/');
    return [ parent, name ];
}

// #endregion

// #region - START -----------------------------------------------------------------------------------------------------

const urlParams = new URLSearchParams(window.location.search);
const video_hash = urlParams.get('hash');

if (!video_hash || urlParams.has('random')) {
    console.log("Getting random video hash ...");
    $.get('/api/get/random-video-hash', (data, status) => {
        if (status === 'success') {
            const params = new URLSearchParams(location.search);
            params.set('hash', data.hash);
            // location.replace(location.pathname + '?' + params.toString())
            window.location.search = params.toString();
        }
    })

} else {
    main(video_hash);

}
