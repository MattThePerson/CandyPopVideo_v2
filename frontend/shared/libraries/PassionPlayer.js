
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

        // video.on('click', () => this.toggle_playback() );
        // video.on('dblclick', () => this.toggle_fullscreen() );
        
        /* click interactions interactions */
        this.addClickEventListeners();


        /* progress bar */
        const progress_bar = this.$('#progress-bar');

        video.on('timeupdate', (event) => {
            const ts = event.timeStamp
            const perc = ts/1000 / video_duration * 100;
            progress_bar.width( perc+'%' );
        })
        

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
            <div id="progress-bar-wrapper">
                <div id="progress-bar"></div>
            </div>
        `;
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

    toggle_playback() {
        (this.video.paused) ? this.video.play() : this.video.pause();
    }

    toggle_fullscreen() {
        const container = this.video.parentElement;
        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => console.error(err));
        } else {
            document.exitFullscreen();
        }
    }

    /* responsive toggle playback but lenient toggle fullscreen */
    addClickEventListeners() {
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
                }, 75);
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

