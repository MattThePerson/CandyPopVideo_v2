import { makeApiRequestGET } from "../../shared/util/request.js";
import { loadSRTasVTT } from "../../shared/util/vtt.js";


export function load_video_player(video_hash, video_data, url_params) {
    
    
    // console.log("CREATING VIDEO PLAYER");
    
    /* CREATE PLAYER */

    // @ts-ignore
    const player = new Playerjs({
        id: "player",
        title: video_data.filename,
        file: '/media/get/video/' + video_hash,
        poster: `/media/get/poster/${video_hash}?t=${Date.now()}`,// `../static/preview/${videodata.poster.replace('\\', '/')}`,
        //autoplay: true,          // Autoplay the video (if allowed by the browser)
        preload: 'auto',          // Preload the video to reduce buffering (try "metadata" or "none" if performance is still an issue)
        seek: 5,                  // Seeks the video to the nearest 5 seconds
        mute: false 
    });

    let playerStartTime = url_params.get('time');
    
    function setPlayerTime() {
        // console.log('in setPlayerTime()');
        let currentTime = player.api('time');
        if (currentTime !== false) {
            if (playerStartTime) {
                console.log('setting time to: ' + playerStartTime);
                player.api('seek', playerStartTime);
            }
            if (url_params.get('autoplay')) {
                // player.api('play');
            }
        } else {
            setTimeout(setPlayerTime, 100);
        }
    }
    setPlayerTime();
    

    /* REQUEST SEEK THUMBS */

    const thumbnailContainer = document.getElementById('thumbnail-container');
    const playerContainer = document.getElementById('player-container');
    
    const thumbActivateThickness_default = 40;
    let thumbActivateThickness = thumbActivateThickness_default;

    
    $.get("/media/ensure/seek-thumbnails/"+video_hash, (data, status) => {
        if (status === "success") {
            loadThumbnails(playerContainer, thumbnailContainer, video_hash, video_data, thumbActivateThickness);
        }
    })

    /** @type {HTMLVideoElement} */
    const video_el = document.querySelector('#player video');
    // return;
    loadSRTasVTT(`/media/get/subtitles/${video_hash}`, (url) => {
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
    

    /* EVENT LISTENERS */

    /** @type {*} */
    const progressionBarCanvas = document.getElementById('progression-bar-canvas'); // for showing progression when controlls disappear in fullscreen
    const progressionBarCanvas_thickness = 3.5;
    progressionBarCanvas.style.display = 'block';
    progressionBarCanvas.style.position = 'fixed';
    progressionBarCanvas.style.bottom = '0';
    progressionBarCanvas.height = progressionBarCanvas_thickness;
    progressionBarCanvas.width = window.screen.width;

    
    function onFullscreenChange() {
        // @ts-ignore
        const fullscreenElement = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
        if (fullscreenElement) {
            fullscreenElement.appendChild(thumbnailContainer);
            fullscreenElement.appendChild(progressionBarCanvas);
            progressionBarCanvas.style.display = 'block';
            startProgressBar(player, progressionBarCanvas, progressionBarCanvas_thickness);
        } else {
            document.body.appendChild(thumbnailContainer);
            // document.body.appendChild(progressionBarCanvas);
            // progressionBarCanvas.style.display = 'none';
            stopProgressBar();
        }
    }
    document.addEventListener('fullscreenchange', onFullscreenChange);
    document.addEventListener('webkitfullscreenchange', onFullscreenChange);
    document.addEventListener('mozfullscreenchange', onFullscreenChange);
    document.addEventListener('MSFullscreenChange', onFullscreenChange);


    /* CUSTOM PROGRESS BAR */
    // const progress_bar
    
    /* PLAYBACK CHANGE EVENT HANDLERS */

    let last_play_time = null;
    let first_playback = false;

    video_el.addEventListener('play', () => {
        last_play_time = Date.now();
        if (!first_playback) {
            $.post('/api/interact/last-viewed/add/'+video_hash);
            first_playback = true;
        }
    })

    video_el.addEventListener('pause', () => {
        if (last_play_time) {
            const time_played = (Date.now() - last_play_time) / 1000;
            last_play_time = null;
            console.debug(`viewtime: ${time_played}s`);
            $.post(`/api/interact/viewtime/add/${video_hash}/${time_played}`);
        }
    })

    window.addEventListener("beforeunload", function (event) {
        if (!video_el.paused && last_play_time) {
            const time_played = (Date.now() - last_play_time) / 1000;
            last_play_time = null;
            console.debug(`viewtime: ${time_played}s`);
            $.post(`/api/interact/viewtime/add/${video_hash}/${time_played}`);
        }
    });
    
}


//region - HELPERS -----------------------------------------------------------------------------------------------------

async function loadThumbnails(playerContainer, thumbnailContainer, video_hash, video_data, thumbActivateThickness) {

    console.debug('loading seek thumbs');

    const videoElement = document.querySelector('#player video');
    const videoDuration = video_data.duration_seconds;

    // Load and parse the VTT file
    const response = await fetch(`/static/preview-media/0x${video_hash}/seekthumbs.vtt`);
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

    const spriteUrl = `/static/preview-media/0x${video_hash}/seekthumbs.jpg`;

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


// Function to draw progress bar
// function drawProgressBar(progressionBarCanvas, progressionBarCanvas_thickness, currentTime, duration) {
//     const ctx = progressionBarCanvas.getContext('2d');
//     ctx.clearRect(0, 0, progressionBarCanvas.width, progressionBarCanvas.height); // Clear the canvas
//     const progressPercent = currentTime / duration;
//     ctx.fillStyle = '#a278';
//     ctx.fillRect(0, 0, progressPercent * document.fullscreenElement.clientWidth, progressionBarCanvas_thickness);
// }

let progressInterval;

function startProgressBar(player, progressionBarCanvas, progressionBarCanvas_thickness) {
    progressInterval = setInterval(() => {
        const currentTime = player.api('time');
        const duration = player.api('duration');
        if (!isNaN(duration)) {
            // drawProgressBar(progressionBarCanvas, progressionBarCanvas_thickness, currentTime, duration);
            const ctx = progressionBarCanvas.getContext('2d');
            ctx.clearRect(0, 0, progressionBarCanvas.width, progressionBarCanvas.height); // Clear the canvas
            const progressPercent = currentTime / duration;
            ctx.fillStyle = '#a278';
            ctx.fillRect(0, 0, progressPercent * document.fullscreenElement.clientWidth, progressionBarCanvas_thickness);
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

