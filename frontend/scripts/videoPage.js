
/* HANDLE RANDOM VIDEO API REQUEST */

if (urlParams.get('random') || !urlParams.get('hash')) {
    console.log("Getting random video hash ...");
    makeApiRequestGET('get-random-video', [], (arg) => {
        const urlParams = new URLSearchParams({'hash' : arg.hash});
        url = "videoPage.html?" + urlParams.toString();
        console.log("Redirecting to: " + url);
        window.location.href = url;
    });
}

let autoplayVideo = false;
if (urlParams.get('autoplay'))
    autoplayVideo = true;


/* FUNCTIONS */

function generateThumbnailName(index) {
    let start = 'seekthumb';
    let digits = 4;
    const paddedIndex = String(index).padStart(digits, '0'); // Pad the index with zeros
    return `${start}${paddedIndex}`;
}

function getSeekThumbnailInterval(duration_sec) {
    let interval = Math.floor( (5/1920) * duration_sec )
    if (interval < 1) interval = 1;
    return interval;
}

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
function loadThumbnails() {

    // create seek thumbnails
    videoDuration = videodata_global.duration_seconds;
    seekThumbnailInterval = getSeekThumbnailInterval(videoDuration);
    i = 1;
    for (let sec = seekThumbnailInterval; sec < videoDuration; sec += seekThumbnailInterval) {
        const thumbnail = document.createElement("div");
        const fn = generateThumbnailName(i++);
        thumbnail.id = fn;
        thumbnail.className = 'seekthumbnail';
        thumbnail.innerHTML = `<img src="media/videos/0x${videoHash}/seekthumbs/${fn}.jpg" alt="Thumbnail at ${sec} seconds">`;
        thumbnailContainer.appendChild(thumbnail);
    }

    // mousemove event listener
    const videoElement = document.querySelector('#player video');
    playerContainer.addEventListener('mousemove', (event) => {
        thumbnailContainer.style.display = 'block';
        thumbnailContainer.style.width = Math.floor(videoElement.clientHeight * 0.4) + 'px';
        document.querySelectorAll('.seekthumbnail').forEach( div => {
            let img = div.querySelector('img');
            img.style.display = 'none';
        });
        const rect = videoElement.getBoundingClientRect();
        const posX = event.clientX - rect.left;
        const posY = event.clientY - rect.top;
        const diff = videoElement.clientHeight - posY;
        let thumbnailReferenceContainer = playerContainer;
        if (document.fullscreenElement) {
            thumbnailReferenceContainer = document.fullscreenElement;
        }
        if (diff <= thumbActivateThickness) {
            thumbActivateThickness = 40;
            const hoverTime = (posX / rect.width) * videoDuration;
            let seekThumbIndex = Math.floor(hoverTime / seekThumbnailInterval) + 1;
            let seekThumbId = generateThumbnailName(seekThumbIndex);
            let thumbnail = document.getElementById(seekThumbId);
            let img = thumbnail.querySelector('img');
            img.style.display = 'block';
            let thumb_x_disp = event.clientX-img.clientWidth/2;
            if (thumb_x_disp < 0) thumb_x_disp = 5;
            let max_x_dist = thumbnailReferenceContainer.clientWidth - img.clientWidth - 26;
            if (thumb_x_disp > max_x_dist) thumb_x_disp = max_x_dist;
            thumbnailContainer.style.left = `${thumb_x_disp}px`;
            let thumb_y_disp = thumbnailReferenceContainer.clientHeight - img.clientHeight
            if (document.fullscreenElement) {
                thumb_y_disp = window.innerHeight - img.clientHeight - 75;
            }
            thumbnailContainer.style.top = `${thumb_y_disp}px`;
        } else {
            thumbActivateThickness = thumbActivateThickness_default;
        }
    });

    playerContainer.addEventListener('mouseout', () => {
        thumbnailContainer.style.display = 'none';
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


/* GLOBAL VARIABLES */

let videoDuration = null;
let seekThumbnailInterval = null;
const thumbActivateThickness_default = 13;
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


let videodata_global;
const videoHash = urlParams.get('hash');
console.log("Video hash: " + videoHash);

let video_metadata_loaded = false;
let related_videos_load_amount = 8;
let related_videos_loaded = 0;

let favouritesButton = document.getElementById('add-favourite-button')


/* EVENT LISTENERS */

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


/* API REQUEST */

// GET VIDEO DATA
makeApiRequestGET('get-video', [videoHash], videodata => {
    videodata_global = videodata;
    console.log(videodata);
    
    // let pathComponents = videodata.path.split("\\");
    // let filename = pathComponents.pop();
    // let encodedFilename = encodeURIComponent(filename);
    // let encodedPath = pathComponents.join("/") + "/" + encodedFilename;
    
    // Create player
    player = new Playerjs({
        id: "player",
        title: videodata.filename,
        file: 'video/' + videoHash,
        poster: `media/videos/0x${videoHash}/${videodata['poster'].replace('\\', '/')}`,
        //autoplay: true,          // Autoplay the video (if allowed by the browser)
        preload: 'auto',          // Preload the video to reduce buffering (try "metadata" or "none" if performance is still an issue)
        seek: 5,                  // Seeks the video to the nearest 5 seconds
        mute: false 
    });

    let playerStartTime = urlParams.get('time');
    
    function setPlayerTime() {
        console.log('in setPlayerTime()');
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
    document.title = videodata.actor + ' - ' + videodata.title;
    const header = document.querySelector(".video-header");
    header.querySelector('.title').innerText = videodata.title;
    header.querySelector('.actor').innerText = videodata.actor;
    header.querySelector('.studio').innerText = videodata.studio;
    header.querySelector('.collection').innerText = videodata.collection;
    header.querySelector('.year').innerText = videodata.date || null;
    header.querySelector('.duration').innerText = videodata.duration;
    header.querySelector('.resolution').innerText = videodata.resolution + 'p';
    header.querySelector('.bitrate').innerText = Math.round(videodata.bitrate/100)/10 + 'mb';
    header.querySelector('.fps').innerText = videodata.FPS + 'fps';

    // configure favourites button
    favouritesButton.addEventListener('click', (args) => {
        if (videodata['is_favourite']) {
            console.log("removing favourite: ", videoHash);
            makeApiRequestGET('remove-favourite', [videoHash], () => {
                toggle_favourites_button_OFF(favouritesButton);
                videodata['is_favourite'] = false;
            });
        } else {
            console.log("adding favourite: ", videoHash);
            makeApiRequestGET('add-favourite', [videoHash], () => {
                toggle_favourites_button_ON(favouritesButton);
                videodata['is_favourite'] = true;
            });
        }
    });
    toggle_favourites_button_OFF(favouritesButton);
    if (videodata['is_favourite']) {
        toggle_favourites_button_ON(favouritesButton);
    }

    // load related videos

    makeApiRequestGET('get-similar-videos', [videodata.hash, 1, related_videos_load_amount], search_results => {
        generate_results(search_results);
    });
    related_videos_loaded += related_videos_load_amount;

    // expand related results button
    document.getElementById('expand-results-button').addEventListener('click', arg => {
        console.log('Loading more related videos. Getting from index: ' + related_videos_loaded);
        makeApiRequestGET('get-similar-videos', [videodata.hash, related_videos_loaded+1, related_videos_load_amount], search_results => {
            generate_results(search_results);
        });
        related_videos_loaded += related_videos_load_amount;
    });

    // request seek thumbnails
    makeApiRequestGET('confirm-seek-thumbnails', [videoHash], loadThumbnails);
});



/* EVENT HANDLERS, UNUSED */

/* document.getElementById('show-video-display-button').addEventListener('click', arg => {
    console.log("Making request for large teaser");
    makeApiRequestGET('confirm-teaser-large', [videodata.hash], () => {
        console.log("HELLOOOO");
        const backgroundVid = document.querySelector(".background-video");
        backgroundVid.querySelector('source').src = `media/videos/0x${videodata.hash}/teaser_large.mp4`;
        backgroundVid.load();
        backgroundVid.play();
    });
}); */

