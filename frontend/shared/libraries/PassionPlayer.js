
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
        this.markers_get = markers_get;
        this.markers_post = markers_post;
        this.keybind_override_elements = keybind_override_elements;
        this.dev_styles_path = styles; // dev
        this.quiet = quiet;

        this.root_element;
        this.shadow;
        this.video;
        
        /* seek thumbs */
        this.seekThumbsContainer;
        this.seekThumbsSprites; // list of sprites objects
        this.seekThumbsSpritesheetSize;
        
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
        
        this.hydrate();
        
        // add keybinds ...
        this.addKeybinds(this.keybind_override_elements);

        // add event listeners
        this.addEventListeners();
        
        // load seek thumbs ...
        if (this.seek_thumbs_vtt_src) {
            this.loadSeekThumbnails(this.seek_thumbs_vtt_src);
        }

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
    
    
    hydrate() {

        /* set video duration */
        this.$('.time-duration-container .duration').text( this.format_time(this.video.duration) );
        
    }
    
    addEventListeners() {

        const video = this.$('video');

        /* click interactions interactions */
        this.addVideoClickEventListeners();

        /* progress bar */
        const progress_bar_container = this.shadow.querySelector('#progress-bar-default');
        this.addDefaultProgressBarEventListeners(progress_bar_container);
        
    }

    /* responsive toggle playback but lenient toggle fullscreen */
    addVideoClickEventListeners() {
        let pb_flag = false; // playback
        let fs_flag = false; // fullscreen
        this.video.addEventListener('click', () => {
            if (pb_flag === false && fs_flag === false) {
                pb_flag = true;
                fs_flag = true;
                setTimeout(() => {
                    if (pb_flag) {
                        this.toggle_playback();
                        pb_flag = false;
                    }
                }, 175);
                setTimeout(() => {fs_flag = false}, 350);
            
            } else if (fs_flag) {
                if (pb_flag === false) { // clicked after pb toggled (125ms)
                    this.toggle_playback();
                    console.log('hiding');
                    console.log(this.$('.pp-icon').length);
                    this.$('.pp-icon').each((_, el) => { el.style.display = 'none' });
                }
                this.toggle_fullscreen();
                pb_flag = false;
                fs_flag = false;
            }
        });
    }

    addDefaultProgressBarEventListeners(container) {

        const progress_bar_container = this.$(container);
        const progress_bar = progress_bar_container.find('.progress-bar');
        const video_duration = this.video.duration;
        
        $(this.video).on('timeupdate', () => {
            const ts = this.video.currentTime;
            const perc = ts / video_duration * 100;
            progress_bar.width( perc+'%' );

            this.$('.time-duration-container .current').text( this.format_time(this.video.currentTime) );
        })

        /* toggle container height */
        progress_bar_container.on('mouseenter', () => progress_bar_container.css('height', '38px'));
        progress_bar_container.on('mouseleave', () => progress_bar_container.css('height', '12px'));

        progress_bar_container.on('click', (e) => {
            const rect = progress_bar_container[0].getBoundingClientRect();
            const x = e.clientX - rect.left; // x relative to element
            const perc = x / rect.width;
            this.setPlaybackTime(perc, progress_bar[0]);
            console.log(this.video.currentTime, perc*100);
        });
        
        progress_bar_container.on('mousemove', (e) => {
            const rect = progress_bar_container.get(0).getBoundingClientRect();
            const perc = ((e.clientX - rect.left) / rect.width) * 100;
            this.updateSeekThumbnail(e.clientX, perc);
        });
        progress_bar_container.on('mouseleave', () => this.hideSeekThumbnail());
        
    }
    
    
    // #endregion
    
    // #region - html --------------------------------------------------------------------------------------------------

    getHTML() {
        return /* html */ `
            <video
                src=${this.src}
                loop
                muted
                preload="metadata"
            ></video>

            <!-- video controls (things that go invisible) -->
            <div class="video-controls">
                
                <!-- default progress bar -->
                <div id="progress-bar-default" class="progress-bar-interact-zone">
                    <div class="progress-bar-wrapper">
                        <div class="progress-bar"></div>
                    </div>
                </div>

                <!-- alt progress bar -->
                <div id="progress-bar-alt">
                    <div id="playhead"></div>
                </div>

                <div class="time-duration-container">
                    <div class="current">xx.xx.xx</div>
                    <span>/</span>
                    <div class="duration"></div>
                </div>

            </div>

            <!-- <div id="progress-bar-persistent"></div> -->
            <!-- <div class="tooltip"></div> -->

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
            </div>

            <!-- seek thumbs container -->
            <div id="seek-thumbs-container">
                <div class="time"></div>
                <div class="seek-thumbnail"></div>
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
                // || true
            ;
            
            if (!ignore_keydown) {

                const key = e.shiftKey ? 's-'+e.code : e.code;
                
                switch (key) {
                    case 'Space':
                        e.preventDefault();
                        this.toggle_playback();
                        break;
                    case 'KeyF':
                        this.toggle_fullscreen();
                        break;
                }
                
            }
            
        });
        
    }

    
    // #endregion
    
    // #region - SEEK THUMBS ---------------------------------------------------------------------------------------------------
    
    updateSeekThumbnail(mouse_x, video_perc) {
        if (this.seekThumbsContainer) {
            const cont = $(this.seekThumbsContainer);
            cont.show();

            /* x translate */
            const cont_wid = parseInt(cont.css('width'));
            let x_translate = mouse_x-cont_wid/2;
            const padding = 8;
            x_translate = Math.max(x_translate, padding);
            const window_wid = document.documentElement.clientWidth;
            x_translate = Math.min(x_translate, window_wid-cont_wid-padding);
            cont.css('left', x_translate + 'px');
            
            /* background image shift */
            const holder = cont.find('.seek-thumbnail');
            const scaleFactor = (parseInt(holder.css('height')) / this.seekThumbsSprites[0].h);
            holder.css(
                'backgroundSize',
                (this.seekThumbsSpritesheetSize.w * scaleFactor) + 'px ' + (this.seekThumbsSpritesheetSize.h * scaleFactor) + 'px'
            )

            const thumbIndex = Math.floor(video_perc/100 * (this.seekThumbsSprites.length));
            // console.log(thumbIndex, this.seekThumbsSprites.length, video_perc);
            const sprite = this.seekThumbsSprites[thumbIndex];
            holder.css(
                'backgroundPosition',
                `-${sprite.x*scaleFactor}px -${sprite.y*scaleFactor}px`
            )

            /* update time */
            this.$('#seek-thumbs-container .time').text( this.format_time(this.video.duration * video_perc/100) );

            // console.table(thumbIndex, video_perc);
            
        }
    }

    hideSeekThumbnail() {
        if (this.seekThumbsContainer) {
            $(this.seekThumbsContainer).hide();
        }
    }
    
    async loadSeekThumbnails(vtt_src) {

        const response = await fetch(vtt_src)
        if (response.status !== 200) {
            throw new Error(`Unable to fetch seek thumbnail webvtt from: ${vtt_src}`);
        }
        const vtt = await response.text();
        const sprites = this.parseVTT(vtt);
        // console.log(sprites);

        // get image and wait to load
        const spritesheet_src = vtt_src.replace('.vtt', '.jpg');
        const img = new Image();
        img.src = spritesheet_src;

        await new Promise(resolve => {
            img.onload = resolve;
        });

        this.seekThumbsSpritesheetSize = { w: img.naturalWidth, h: img.naturalHeight };
        
        /** @type {HTMLElement} */
        this.seekThumbsContainer = this.shadow.querySelector('#seek-thumbs-container');
        /** @type {HTMLElement} */
        const seekThumbsHolder = this.seekThumbsContainer.querySelector('.seek-thumbnail');
        seekThumbsHolder.style.backgroundImage = `url("${spritesheet_src}")`;
        seekThumbsHolder.style.backgroundRepeat = 'no-repeat';

        /* determine  */
        const thumbAspectRatio = sprites[0].w / sprites[0].h;
        seekThumbsHolder.style.width = (thumbAspectRatio * seekThumbsHolder.clientHeight) + 'px';

        /* make visible but hidden */
        this.seekThumbsContainer.style.visibility = 'visible';
        this.seekThumbsContainer.style.display = 'none';
        
        this.seekThumbsSprites = sprites;

        
    }

    // Helper function to parse VTT files containing sprite metadata
    parseVTT(vttText) {
        const sprites = [];
        const lines = vttText.split('\n');
        
        // The VTT format we're expecting has entries like:
        // 00:00:00.000 --> 00:00:00.000
        // xywh=0,0,160,90
        
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('xywh=')) {
                const coords = lines[i].split('xywh=')[1].split(',');
                if (coords.length === 4) {
                    sprites.push({
                        x: parseInt(coords[0]),
                        y: parseInt(coords[1]),
                        w: parseInt(coords[2]),
                        h: parseInt(coords[3])
                    });
                }
            }
        }
        
        return sprites;
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

    format_time(seconds_float) {

        const hours = Math.floor( seconds_float/3600 );
        const minutes = Math.floor( (seconds_float - hours*3600)/60 );
        const seconds = Math.floor( seconds_float - hours*3600 - minutes*60 );
        
        let hours_str = hours.toString();
        let minutes_str = minutes.toString();
        let seconds_str = seconds.toString();
        
        hours_str = (hours_str.length == 2) ? hours_str : '0' + hours_str;
        minutes_str = (minutes_str.length == 2) ? minutes_str : '0' + minutes_str;
        seconds_str = (seconds_str.length == 2) ? seconds_str : '0' + seconds_str;
        
        let fmt = minutes_str + ':' + seconds_str;

        if (hours > 0) {
            fmt = hours_str + ':' + fmt;
        }

        return fmt;
        
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



