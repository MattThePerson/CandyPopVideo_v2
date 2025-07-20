
/* Creates a player */
export class PassionPlayer {

    constructor({
        player_id,
        src,
        poster=null,
        title=null,
        seek_thumbs_vtt_src=null,
        subtitles_srt_src=null,
        autoplay=true,
        mute=false,
        preload='auto',
        // seek: 5,  // Seeks the video to the nearest 5 seconds
        markers_get=null,  // api route to get timeline markers 
        markers_post=null,
        keybind_override_elements=null,  // array of selectors for elements that will disable keybinds when focused
        styles=null,  // path to styles file (dev)
        quiet=true,
    }) {
        this.player_id = player_id;
        this.src = src;
        this.poster = poster;
        this.title = title;
        this.seek_thumbs_vtt_src = seek_thumbs_vtt_src;
        this.subtitles_srt_src = subtitles_srt_src;
        this.autoplay = autoplay;
        this.mute = mute;
        this.preload = preload;
        // this.seek = seek;
        this.markers_get = markers_get;
        this.markers_post = markers_post;
        this.keybind_override_elements = keybind_override_elements;
        this.dev_styles_path = styles; // dev
        this.quiet = quiet;

        this.root_element;
        this.shadow;
        this.video;
        
    }

    async init() {

        this.root_element = document.getElementById(this.player_id);
        if (!this.root_element) {
            throw new Error(`Cannot inject Passion Player, no element with id: ${this.player_id}`);
        }

        this.shadow = this.root_element.attachShadow({ mode: 'open' });

        await this.addStyles(this.shadow, this.dev_styles_path);
        this.addHTML(this.shadow);

        /* wait for video to load */
        await new Promise(resolve => {
            this.$('video').one('loadeddata', resolve);
        });
        this.video = this.shadow.querySelector('video');
        this.log('video loaded');
        
        // add keybinds ...
        this.addKeybinds(this.keybind_override_elements);

        // add event listeners
        this.addEventListeners();
        
        // load seek thumbs ...

        // load subtitles ...
        
        // load markers ...

        // ...
    }

    addHTML(shadow) {
        const player = document.createElement('div');
        player.className = 'PassionPlayer';
        player.innerHTML = this.getHTML();
        shadow.appendChild(player);
    }

    async addStyles(shadow, styles_path) {
        let css = this.getStyles();
        if (styles_path) {
            const response = await fetch(styles_path);
            if (response.status !== 200) {
                throw new Error(`Styles not found: ${styles_path}`);
            }
            css = await response.text();
        }
        const style = document.createElement('style');
        style.textContent = css;
        shadow.appendChild(style);
    }
    

    // #region - HANDLERS ----------------------------------------------------------------------------------------------
    
    
    addEventListeners() {

        const video = this.$('video');
        const video_duration = video.get(0).duration;


        /* click interactions interactions */
        this.addVideoClickEventListeners();


        /* progress bar */
        const progress_bar = this.$('#progress-bar');
        const progress_bar_interact = this.$('.progress-bar-interact-zone');

        video.on('timeupdate', (event) => {
            const ts = this.video.currentTime;
            const perc = ts / video_duration * 100;
            progress_bar.width( perc+'%' );
        })

        progress_bar_interact.on('mouseenter', () => progress_bar_interact.css('height', '38px'));
        progress_bar_interact.on('mouseleave', () => progress_bar_interact.css('height', '12px'));

        progress_bar_interact.on('click', (e) => {
            console.log('clicked');
            const rect = progress_bar_interact[0].getBoundingClientRect();
            const x = e.clientX - rect.left; // x relative to element
            const perc = x / rect.width;
            this.setPlaybackTime(perc, progress_bar[0]);
        });
        
    }
    
    // #endregion
    
    // #region - html --------------------------------------------------------------------------------------------------

    getHTML() {
        return /* html */ `
            <video
                src=${this.src}
                muted
                autoplay
                preload="metadata"
            ></video>
            <!-- video controls -->
            <div class="video-controls">
                <div class="progress-bar-interact-zone">
                    <div id="progress-bar-wrapper">
                        <div id="progress-bar"></div>
                    </div>
                </div>
            </div>

            <!-- icons -->
            <div class="play-pause-indicator">
                <svg class="pp-icon pause-icon" width="64px" height="64px" viewBox="-1 0 8 8" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                    <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><g id="Dribbble-Light-Preview" transform="translate(-227.000000, -3765.000000)" fill="#000000"><g id="icons" transform="translate(56.000000, 160.000000)">
                        <path d="M172,3605 C171.448,3605 171,3605.448 171,3606 L171,3612 C171,3612.552 171.448,3613 172,3613 C172.552,3613 173,3612.552 173,3612 L173,3606 C173,3605.448 172.552,3605 172,3605 M177,3606 L177,3612 C177,3612.552 176.552,3613 176,3613 C175.448,3613 175,3612.552 175,3612 L175,3606 C175,3605.448 175.448,3605 176,3605 C176.552,3605 177,3605.448 177,3606" id="pause-[#1006]"></path>
                    </g></g></g>
                </svg>

                <svg class="pp-icon play-icon" width="64px" height="64px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21.4086 9.35258C23.5305 10.5065 23.5305 13.4935 21.4086 14.6474L8.59662 21.6145C6.53435 22.736 4 21.2763 4 18.9671L4 5.0329C4 2.72368 6.53435 1.26402 8.59661 2.38548L21.4086 9.35258Z" fill="#1C274C"/>
                </svg>
                
                
                <style>
                    .play-pause-indicator {
                        width: fit-content;
                        height: fit-content;
                        position: absolute;
                        top: calc(50% - 32px);
                        left: calc(50% - 32px);
                        pointer-events: none;
                    }
                    .play-pause-indicator svg path {
                        fill: #fffd;
                    }
                    .NONE {
                        position: absolute; top: 0; left: 0;
                    }
                    .pp-icon {
                        display: none;
                        opacity: 0;
                        background: #0005;
                        border-radius: 50%;
                        padding: 1rem;
                        border: 1px solid #fff4;
                        transform-origin: center;
                        transform: scale(110%);
                        transition:
                            opacity 500ms ease-out,
                            transform 500ms ease-out
                        ;
                    }
                    .pp-icon.shown {
                        opacity: 1;
                        transform: scale(80%);
                        transition: none;
                    }
                </style>

            </div>
        `;
    }


    // #endregion
    
    // #region - KEYBINDS -----------------------------------------------------------------------------------------------

    addKeybinds(keybind_override_elements) {
        
        document.addEventListener('keydown', (e) => {

            const ignore_keydown = false
                || document.activeElement.tagName === 'INPUT'
                // || document.activeElement.className
            ;

            if (!ignore_keydown) {

                let key = e.code;
                if (e.shiftKey) {
                    key = 's-' + key;
                }
                // console.log(key);
                
                switch (key) {
                    case 'KeyF':
                        console.log('f has been pressed');
                        break;
                }
                
            }
            
        });
        
    }

    
    // #endregion
    
    // #region - HELPERS -----------------------------------------------------------------------------------------------

    $(selector) {
        return $(this.shadow).find(selector);
    }

    log(msg) {
        if (!this.quiet) {
            console.log(msg);
        }
    }

    /* get playback time as perc between 0 -> 1 */
    setPlaybackTime(perc, progress_bar) {
        const newTime = this.video.duration * perc;
        this.video.currentTime = newTime;
        progress_bar.style.width = `${perc * 100}%`;
    }

    /* responsive toggle playback but lenient toggle fullscreen */
    addVideoClickEventListeners() {
        let pb_flag = false; // playback
        let fs_flag = false; // fullscreen
        this.video.addEventListener('click', () => {
            const curr = Date.now()
            if (pb_flag === false && fs_flag === false) {
                pb_flag = true
                fs_flag = true
                setTimeout(() => {
                    if (pb_flag) {
                        console.log('click');
                        this.toggle_playback();
                        pb_flag = false;
                    }
                }, 125);
                setTimeout(() => {fs_flag = false}, 350);
            
            } else if (fs_flag) {
                if (pb_flag === false) { // clicked after 75ms
                    this.toggle_playback();
                }
                this.toggle_fullscreen();
                pb_flag = false;
                fs_flag = false;
            }
        });
    }

    toggle_playback() {
        (this.video.paused) ? this.playVideo() : this.pauseVideo();
    }

    pauseVideo() {
        this.video.pause();
        this.flashPPIndicator('.pause-icon');
    }

    playVideo() {
        this.video.play();
        this.flashPPIndicator('.play-icon');
    }

    flashPPIndicator(selector) {
        const play_icon = this.$('.play-icon');
        const pause_icon = this.$('.pause-icon');
        play_icon.hide();
        pause_icon.hide();
        void play_icon.get(0).offsetWidth; // Force reflow
        void pause_icon.get(0).offsetWidth; // Force reflow
        
        const flash_icon = this.$(selector);
        flash_icon.show();
        flash_icon.addClass('shown');
        setTimeout(() => flash_icon.removeClass('shown'), 1);
    }

    toggle_fullscreen() {
        const container = this.video.parentElement;
        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => console.error(err));
        } else {
            document.exitFullscreen();
        }
    }

    
    
    // #endregion

    // #region - css ---------------------------------------------------------------------------------------------------
    
    getStyles() {
        return /* css */`
            .PassionPlayer {
                height: 100%;
                width: 100%;
                background: purple;
                display: flex;
                justify-content: center;
            }
            
            video {
                height: 100%;
            }
        `;
    }


    // #endregion
}








/* load subtitles */
async function loadSRTasVTT(srtUrl, video_el) {
    const response = await fetch(srtUrl);
    let srt = await response.text();

    // console.log(srt);
    
    // Basic .srt → .vtt conversion
    let vtt = 'WEBVTT\n\n' + srt
        .replace(/\r/g, '')
        .replace(/(\d+)\n(\d{2}:\d{2}:\d{2}),(\d{3}) --> (\d{2}:\d{2}:\d{2}),(\d{3})/g,
                '$1\n$2.$3 --> $4.$5');

    const blob = new Blob([vtt], { type: 'text/vtt' });
    const url = URL.createObjectURL(blob);

    const track = document.createElement('track');
    track.kind = 'subtitles';
    track.label = 'English';
    track.srclang = 'en';
    track.src = url;
    track.default = true;

    video_el.appendChild(track);
}

