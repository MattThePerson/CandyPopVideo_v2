
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
        styles=null,  // path to styles file
        markers_get=null,  // api route to get timeline markers 
        markers_post=null,
        keybind_override_elements=null,  // array of selectors for elements that will disable keybinds when focused
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
        this.styles_path = styles;
        this.markers_get = markers_get;
        this.markers_post = markers_post;
        this.keybind_override_elements = keybind_override_elements;

        this.root_element = document.getElementById(this.player_id);
        if (!this.root_element) {
            throw new Error(`Cannot inject Passion Player, no element with id: ${this.player_id}`);
        }

        this.shadow = this.root_element.attachShadow({ mode: 'open' });

        this.shadow.appendChild( this.getStyles(this.styles_path) );
        this.shadow.appendChild( this.getHTML() );

        // load markers ...

        // add keybinds ...

        // 
    }
    

    /* - get styles ------------------------------------------------------------------------------------------------- */
    async getStyles(styles_path) {
        let css;
        if (styles_path) {
            const response = await fetch(styles_path);
            css = await response.text();
        } else {
            css = /* css */`
            
            `;
        }
        const style = document.createElement('style');
        style.textContent = css;
        return style;
    }


    /* - get html --------------------------------------------------------------------------------------------------- */
    getHTML() {
        const player = document.createElement('div');
        player.className = 'player';
        player.innerHTML = /* html */`

        `;
        return player;
    }

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

