
import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET, makeApiRequestPOST } from '../../shared/util/request.js';
import { generate_results_OLD } from '../../shared/util/search_OLD.js';
import { generate_results } from '../../shared/util/load.js';
import { loadSRTasVTT } from '../../shared/util/vtt.js';

injectComponents();


const urlParams = new URLSearchParams(window.location.search);

//region - HANDLE RANDOM VIDEO REQUEST ---------------------------------------------------------------------------------

if (urlParams.get('random') || !urlParams.get('hash')) {
    console.log("Getting random video hash ...");
    makeApiRequestGET('/api/get/random-video-hash', [], (arg) => {
        const params = new URLSearchParams(location.search);
        params.set('hash', arg.hash);
        location.replace(location.pathname + '?' + params.toString())
    });
}

let autoplayVideo = false;
if (urlParams.get('autoplay'))
    autoplayVideo = true;


//region - FUNCTIONS ---------------------------------------------------------------------------------------------------


// the video IS a favourite
function toggle_favourites_button_ON(butt) {
    favouritesButton.innerText = 'REMOVE FAV';
    favouritesButton.style.background = 'red';
}

// the video IS NOT a favourite
function toggle_favourites_button_OFF(butt) {
    favouritesButton.innerText = 'ADD FAV';
    favouritesButton.style.background = 'orange';
}

// LONG ASS FUNCTION
async function loadThumbnails() {

    const videoElement = document.querySelector('#player video');
    const videoDuration = videodata_global.duration_seconds;

    // Load and parse the VTT file
    const response = await fetch(`/static/preview-media/0x${videoHash}/seekthumbs.vtt`);
    const vttText = await response.text();
    // console.log(vttText);
    
    const cues = [];
    const cueRegex = /(\d+:\d+:\d+\.\d+)\s+-->\s+(\d+:\d+:\d+\.\d+)\s*\n(.+)/g;
    let match;
    while ((match = cueRegex.exec(vttText)) !== null) {
        const [ , start, end, data ] = match;
        const [imgUrl, coords] = data.trim().split('#xywh=');
        const [x, y, w, h] = coords.split(',').map(Number);
        cues.push({ start: toSeconds(start), end: toSeconds(end), x, y, w, h });
    }

    const spriteUrl = `/static/preview-media/0x${videoHash}/seekthumbs.jpg`;

    // Create a single thumbnail div
    const thumbnail = document.createElement('div');
    thumbnail.id = 'sprite-thumbnail';
    thumbnail.style.position = 'absolute';
    // thumbnail.style.display = 'none';
    thumbnail.style.backgroundImage = `url(${spriteUrl})`;
    thumbnail.style.backgroundRepeat = 'no-repeat';
    thumbnail.style.transform = 'scale(0.8)';
    thumbnail.style.transformOrigin = 'bottom';
    thumbnail.style.outline = "1px solid white";
    thumbnail.style.borderRadius = "0.5rem";
    thumbnailContainer.appendChild(thumbnail);

    playerContainer.addEventListener('mousemove', (event) => {
        const rect = videoElement.getBoundingClientRect();
        const posX = event.clientX - rect.left;
        const posY = event.clientY - rect.top;
        const diff = videoElement.clientHeight - posY;

        if (diff <= thumbActivateThickness) {
            const hoverTime = (posX / rect.width) * videoDuration;
            const cue = cues.find(c => hoverTime >= c.start && hoverTime < c.end);
            if (!cue) return;

            const cue_w = cue.w;
            const cue_h = cue.h;
            
            Object.assign(thumbnail.style, {
                display: 'block',
                width: cue_w + 'px',
                height: cue_h + 'px',
                backgroundPosition: `-${cue.x}px -${cue.y}px`,
            });

            let thumb_x_disp = event.clientX - cue_w / 2;
            if (thumb_x_disp < 0) thumb_x_disp = 5;
            let max_x_dist = playerContainer.clientWidth - cue_w - 26;
            if (thumb_x_disp > max_x_dist) thumb_x_disp = max_x_dist;
            thumbnailContainer.style.left = `${thumb_x_disp}px`;

            let thumb_y_disp = playerContainer.clientHeight - cue_h;
            if (document.fullscreenElement) {
                thumb_y_disp = window.innerHeight - cue_h - 75;
            }
            thumbnailContainer.style.top = `${thumb_y_disp}px`;
        } else {
            thumbnail.style.display = 'none';
        }
    });

    playerContainer.addEventListener('mouseout', () => {
        thumbnail.style.display = 'none';
    });
}


// Fullscreen Progression Bar (Canvas) functions

// Function to draw progress bar
function drawProgressBar(currentTime, duration) {
    const ctx = progressionBarCanvas.getContext('2d');
    ctx.clearRect(0, 0, progressionBarCanvas.width, progressionBarCanvas.height); // Clear the canvas
    const progressPercent = currentTime / duration;
    ctx.fillStyle = '#a278';
    ctx.fillRect(0, 0, progressPercent * document.fullscreenElement.clientWidth, progressionBarCanvas_thickness);
}

let progressInterval;

function startProgressBar() {
    progressInterval = setInterval(() => {
        const currentTime = player.api('time');
        const duration = player.api('duration');
        if (!isNaN(duration)) {
            drawProgressBar(currentTime, duration);
        }
    }, 200);
}

function stopProgressBar() {
    clearInterval(progressInterval);
}


//region - MISC. HELPERS -----------------------------------------------------------------------------------------------

function toSeconds(timeStr) {
    const [h, m, s] = timeStr.split(':');
    return parseInt(h) * 3600 + parseInt(m) * 60 + parseFloat(s);
}


//region - GLOBAL VARIABLES --------------------------------------------------------------------------------------------

let videoDuration = null;
let seekThumbnailInterval = null;
const thumbActivateThickness_default = 40;
let thumbActivateThickness = thumbActivateThickness_default;

const thumbnailContainer = document.getElementById('thumbnail-container');
const playerContainer = document.getElementById('player-container');
let player;

const progressionBarCanvas = document.getElementById('progression-bar-canvas'); // for showing progression when controlls disappear in fullscreen
const progressionBarCanvas_thickness = 3.5;
progressionBarCanvas.style.position = 'fixed';
progressionBarCanvas.style.bottom = '0';
progressionBarCanvas.height = progressionBarCanvas_thickness;
progressionBarCanvas.width = window.screen.width;

let video_metadata_loaded = false;

let favouritesButton = document.getElementById('add-favourite-button')



//region - EVENT LISTENERS ---------------------------------------------------------------------------------------------

// HANDLE FULLSCREEN CHANGE
function onFullscreenChange() {
    const fullscreenElement = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
    if (fullscreenElement) {
        fullscreenElement.appendChild(thumbnailContainer);
        fullscreenElement.appendChild(progressionBarCanvas);
        progressionBarCanvas.style.display = 'block';
        startProgressBar();
    } else {
        document.body.appendChild(thumbnailContainer);
        // document.body.appendChild(progressionBarCanvas);
        progressionBarCanvas.style.display = 'none';
        stopProgressBar();
    }
}
document.addEventListener('fullscreenchange', onFullscreenChange);
document.addEventListener('webkitfullscreenchange', onFullscreenChange);
document.addEventListener('mozfullscreenchange', onFullscreenChange);
document.addEventListener('MSFullscreenChange', onFullscreenChange);


document.addEventListener('keydown', (event) => {
    const videoFilters = ['filter-none', 'filter-vixen-dark'];
    if (event.key.toLowerCase() === 'c') {
        console.log('pressed C');
        const videoEl = document.querySelector('video');
        if (videoEl) {
            const currentFilter = Array.from(videoEl.classList).filter(x => videoFilters.includes(x))[0];
            let filterI = 0;
            if (currentFilter) {
                filterI = videoFilters.indexOf(currentFilter);
            }
            filterI = (filterI + 1) % videoFilters.length;
            const nextFilter = videoFilters[filterI];
            videoEl.classList.remove(currentFilter);
            playerContainer.classList.remove(currentFilter);
            videoEl.classList.add(nextFilter);
            playerContainer.classList.add(nextFilter);
            console.log(currentFilter, filterI);
        }
    }
});


//region - BACKEND REQUEST ---------------------------------------------------------------------------------------------

let videodata_global;
const videoHash = urlParams.get('hash');
console.log("Video hash: " + videoHash);

// GET VIDEO
if (videoHash != null) {

    /* VIDEO DATA */
    makeApiRequestGET('/api/get/video-data', [videoHash], videodata => {
        videodata_global = videodata;
        console.log('videodata:', videodata);
        
        
        // Create player
        player = new Playerjs({
            id: "player",
            title: videodata.filename,
            file: '/media/get/video/' + videoHash,
            poster: `/media/get/poster/${videoHash}`,// `../static/preview/${videodata.poster.replace('\\', '/')}`,
            //autoplay: true,          // Autoplay the video (if allowed by the browser)
            preload: 'auto',          // Preload the video to reduce buffering (try "metadata" or "none" if performance is still an issue)
            seek: 5,                  // Seeks the video to the nearest 5 seconds
            mute: false 
        });
    
        let playerStartTime = urlParams.get('time');
        
        function setPlayerTime() {
            // console.log('in setPlayerTime()');
            let currentTime = player.api('time');
            if (currentTime !== false) {
                if (playerStartTime) {
                    console.log('setting time to: ' + playerStartTime);
                    player.api('seek', playerStartTime);
                }
                if (urlParams.get('autoplay')) {
                    // player.api('play');
                }
            } else {
                setTimeout(setPlayerTime, 100);
            }
        }
        setPlayerTime();
    
        // add scene data to page
        document.title = videodata.primary_actors.join(', ') + ' - ' + videodata.title;
        const header = document.querySelector(".video-header");
        header.querySelector('.title').innerText = videodata.title;
        header.querySelector('.actors').innerText = videodata.actors;
        header.querySelector('.studio').innerText = videodata.studio;
        header.querySelector('.collection').innerText = videodata.collection;
        header.querySelector('.year').innerText = videodata.date || null;
        header.querySelector('.duration').innerText = videodata.duration;
        header.querySelector('.resolution').innerText = videodata.resolution + 'p';
        header.querySelector('.bitrate').innerText = Math.round(videodata.bitrate/100)/10 + 'mb';
        header.querySelector('.fps').innerText = videodata.FPS + 'fps';
    
        /* load related videos */

        const related_videos_load_amount = 8;
        let related_videos_loaded = 0;
        
        const load_related_videos = (start_idx) => {
            makeApiRequestGET('/api/query/get/similar-videos', [videodata.hash, start_idx + 1, related_videos_load_amount], search_results => {
                generate_results_OLD(search_results);
                // generate_results(search_results, )
            });
            return start_idx + related_videos_load_amount
        };
    
        related_videos_loaded = load_related_videos(related_videos_loaded);
        document.getElementById('expand-results-button').addEventListener('click', () => {
            related_videos_loaded = load_related_videos(related_videos_loaded);
        });
    
        /* request seek thumbnails */
        makeApiRequestGET('/media/ensure/seek-thumbnails', [videoHash], loadThumbnails);

        const video_el = document.querySelector('#player video');
        loadSRTasVTT(`/media/get/subtitles/${videoHash}`, (url) => {
            const track = document.createElement('track');
            track.kind = 'subtitles';
            track.label = 'English';
            track.srclang = 'en';
            track.src = url;
            track.default = true;

            video_el.appendChild(track);

            const has_subs_indicator = document.createElement('div');
            has_subs_indicator.classList.add('has-subs-indicator');
            has_subs_indicator.innerHTML = /* html */`
                has subs
                <!-- <div></div> -->
                <style>
                    .has-subs-indicator {
                        position: absolute;
                        bottom: -3rem;
                        left: 1rem;
                        background: red;
                        padding: 0.5rem 1rem;
                    }
                </style>
            `;

            document.querySelector('#player').appendChild(has_subs_indicator);
            
        });
        
    });

    
    /* VIDEO INTERACTIONS */
    makeApiRequestGET('/api/interact/get', [videoHash], video_interactions => {

        console.log('video_interactions:', video_interactions);
        
        // configure favourites button
        favouritesButton.onclick = (args) => {
            if (video_interactions.is_favourite) {
                console.log("removing favourite: ", videoHash);
                makeApiRequestPOST('/api/interact/favourites/remove', [videoHash], () => {
                    toggle_favourites_button_OFF(favouritesButton);
                    video_interactions.is_favourite = false;
                });
            } else {
                console.log("adding favourite: ", videoHash);
                makeApiRequestPOST('/api/interact/favourites/add', [videoHash], () => {
                    toggle_favourites_button_ON(favouritesButton);
                    video_interactions.is_favourite = true;
                });
            }
        };

        toggle_favourites_button_OFF(favouritesButton);
        if (video_interactions.is_favourite) {
            toggle_favourites_button_ON(favouritesButton);
        }
        
    });
    
}
