// @ts-ignore
const $ = window.$;


/* SearchResultCard */
export class MyCard extends HTMLElement {

    constructor() {
        super();
        /* attributes */
        this.USE_VIDEO_TEASERS = (this.getAttribute('use_video_teasers') == 'true')
        this.video_hash = this.getAttribute('video_hash');

        this.video_title = this.getAttribute('video_title');
        this.actors_str = this.getAttribute('actors');
        this.studio = this.getAttribute('studio');
        this.line = this.getAttribute('line');
        this.date_released = this.getAttribute('date_released');
        this.scene_description = this.getAttribute('scene_description');
        this.collection = this.getAttribute('collection');
        this.dvd_code = this.getAttribute('dvd_code');

        this.duration = this.getAttribute('duration');
        this.resolution = this.getAttribute('resolution');
        this.fps = this.getAttribute('fps');
        this.bitrate = parseInt(this.getAttribute('bitrate'));

        this.date_added = this.getAttribute('date_added');
        this.tags_str = this.getAttribute('tags');
        this.filename = this.getAttribute('filename');

        this.card_class = (this.getAttribute('highlighted') == 'true') ? "card highlighted" : "card";
        this.card_width = this.getAttribute('width') || "24rem";
        this.aspect_ratio = this.getAttribute('aspect_ratio') || "16/9";

        /* variables */
        this.actors = this.actors_str.split(',').filter(x => x !== '');
        this.max_initial_actors = 4;

        this.tags = this.tags_str.split(',').filter(x => x !== '')
        this.max_initial_tag_chars = 50;

    }

    disconnectedCallback() {
        console.log("Custom element removed from page.");
    }

    connectedMoveCallback() {
        console.log("Custom element moved with moveBefore()");
    }

    adoptedCallback() {
        console.log("Custom element moved to new page.");
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log(`Attribute ${name} has changed.`);
    }

    connectedCallback() {
        // console.log("Custom element added to page.");
        
        this.attachShadow({ mode: 'open' });
        this.render();
        this.hydrate();
        this.addEventListeners();
    }


    // #region - HYDRATE -----------------------------------------------------------------------------------------------

    hydrate() {
        const $shadow = $(this.shadowRoot);

        /* set thumbnail src */
        $shadow.find('img.thumbnail').attr(
            'src',
            `/media/get/poster/${this.video_hash}?t=${Date.now()}`
        );
        
        /* get teasers */
        if (this.USE_VIDEO_TEASERS) { // teaser video
            const teaser_el = $shadow.find('video.teaser-video');
            teaser_el.addClass('teaser-media');
            teaser_el.attr('src', `/static/preview-media/0x${this.video_hash}/teaser_small.mp4`)
            teaser_el.one('loadedmetadata', () => {
                teaser_el.addClass('loaded');
                $shadow.find('.spinner').hide()
            });

        } else { // teaser thumbs
            const teaser_el = $shadow.find('img.teaser-thumbs');
            teaser_el.addClass('teaser-media');
            this.configure_teaser_thumb_spritesheet(
                `/static/preview-media/0x${this.video_hash}/teaser_thumbs_small.jpg`,
                teaser_el.get(0),
                $shadow.find('.thumb-container').get(0),
                () => {
                    teaser_el.addClass('loaded');
                    $shadow.find('.spinner').hide()
            });

        }

        /* check for subs */
        $.get(`/media/get/subtitles/${this.video_hash}?check=true`, (data, status) => {
            if (status === 'success') {
                $shadow.find('.details-bar .has-subs').show();
            }
        });

        /* GET INTERACTIONS */
        $.get('/api/interact/get/'+this.video_hash, (VIs, status) => {
            if (status === 'success') {
                
                /* favourites button */
                const is_fav_button = $shadow.find('button.is-fav-button');
                is_fav_button.addClass('loaded');
                if (VIs.is_favourite) {
                    is_fav_button.addClass('is-fav');
                    is_fav_button[0].title = `favourite added: ${VIs.favourited_date}`
                }
                /* toggle is favourite */
                is_fav_button.on('click', () => {
                    let change_favourite_route;
                    if (is_fav_button.hasClass('is-fav')) {
                        change_favourite_route = `/api/interact/favourites/remove/${this.video_hash}`;
                    } else {
                        change_favourite_route = `/api/interact/favourites/add/${this.video_hash}`;
                    }
                    $.post(change_favourite_route, (_, status) => {
                        if (status === 'success') {
                            is_fav_button.toggleClass('is-fav');
                        }
                    });
                });
                

                /* other */
                $shadow.find('.details-bar .viewtime').text(this.format_seconds(VIs.viewtime));

                if (VIs.likes > 0) {
                    $shadow.find('.details-bar .likes-span').css('display', 'flex');
                    $shadow.find('.details-bar .likes').text(VIs.likes);
                }
                
                
            }
        });
        
    }
    

    // #endregion
    
    // #region - EVENT LISTENERS ---------------------------------------------------------------------------------------

    addEventListeners() {
        const $shadow = $(this.shadowRoot);

        /* click on collection */
        $shadow.find('.collection').click(event => {
            event.preventDefault();
            window.location.href = '/pages/search/page.html?collection=' + this.getAttribute('collection');
        });

        /* first time hover */
        $shadow.find('.thumb-container').one('mouseenter', () => {
            
            if (this.USE_VIDEO_TEASERS) {
                console.debug('ensuring teaser video');
                $.get('/media/ensure/teaser-small/'+this.video_hash, (data, status) => {
                    if (status === 'success') {
                        const teaser_el = $shadow.find('.teaser-media');
                        teaser_el.attr('src', `/static/preview-media/0x${this.video_hash}/teaser_small.mp4`);
                    }
                })

            } else {
                console.debug('ensuring teaser thumbs');
                $.get('/media/ensure/teaser-thumbs-small/'+this.video_hash, (data, status) => {
                    if (status === 'success') {
                        // console.log('teaser_thumbs ensured!');
                        this.configure_teaser_thumb_spritesheet(
                            `/static/preview-media/0x${this.video_hash}/teaser_thumbs_small.jpg?t=${Date.now()}`,
                            $shadow.find('img.teaser-thumbs').get(0),
                            $shadow.find('.thumb-container').get(0),
                            () => {
                                $shadow.find('img.teaser-thumbs').addClass('loaded');
                                $shadow.find('.spinner').hide()
                        });
                    }
                });
            }

        })

        /* add remaining actors/tags */
        const add_actors_button = $shadow.find('.add-remaining-actors-button');
        add_actors_button.on('click', async () => {
            add_actors_button.remove();
            const actors_to_add = this.actors.slice(this.max_initial_actors);
            for (let i = 0; i < actors_to_add.length; i++) {
                const actor = actors_to_add[i];
                $shadow.find('.actors-bar').append(/* html */`
                    ${ (i === 0) ? "" : "<span></span>" }
                    <a href="/pages/search/page.html?actor=${actor}">
                        ${actor}
                    </a>
                `);
                await this.sleep(25);
            }
        });

        const add_tags_button = $shadow.find('.add-remaining-tags-button');
        add_tags_button.on('click', async () => {
            add_tags_button.remove();
            const [_, tags_to_add] = this.filter_tags(this.tags, this.max_initial_tag_chars);
            // tags_to_add.forEach(async (x) => {
            for (let x of tags_to_add) {
                $shadow.find('.tags-bar').append(/* html */ `
                    <a 
                        href="/pages/search/page.html?tags=${x}"
                        style="${this._get_tag_color(x)}"
                    >
                        ${x}
                    </a>
                `);
                await this.sleep(25);
            }
        });

    }


    // #endregion
    
    // #region - RENDER ------------------------------------------------------------------------------------------------

    render() {

        this.duration = this.duration.startsWith("0:") ? this.duration.substring(2) : this.duration;

        const date_released_fmt = this.date_released.replace(/-/g, '.');

        // studios html
        const studios = [this.studio, this.line].filter(el => (el !== null && el !== 'null' && el !== ''));
        const studios_html = studios.map((x, idx) =>
            `
            ${ (idx === 0) ? "" : "<span></span>" }
            <a href="/pages/search/page.html?studio=${x}">
                ${x}
            </a>`
        ).join('\n')
        
        // actors html
        const actors_to_add = this.actors.slice(0, this.max_initial_actors);
        let actors_html = actors_to_add.map((x, idx) => /* html */`
            ${ (idx === 0) ? "" : "<span></span>" }
            <a href="/pages/search/page.html?actor=${x}">
                ${x}
            </a>
        `).join('\n');
        if (this.actors.length > this.max_initial_actors) {
            actors_html += /* html */`
                <span></span>
                <a style="cursor: pointer; color: #888;" class="add-remaining-actors-button">
                    ${this.actors.length - this.max_initial_actors} more
                </a>
            `;
        }

        // tags html
        const [tags_to_add, tags_to_add_later] = this.filter_tags(this.tags, this.max_initial_tag_chars)
        let tags_html = tags_to_add.map((x, idx) => /* html */`
            <a 
                href="/pages/search/page.html?tags=${x}"
                style="${this._get_tag_color(x)}"
            >
                ${x}
            </a>
        `).join('\n')
        if (tags_to_add_later.length > 0) {
            tags_html += /* html */ `
                <a 
                    class="add-remaining-tags-button"
                    style="cursor: pointer; background: #222; color: #ccc !important;"
                >
                    ${tags_to_add_later.length} more
                </a>
            `;
        }

        // title
        let title_fmt = this.video_title.replace(';', ':');
        if (this.dvd_code !== 'null' && this.dvd_code !== "") title_fmt = `[${this.dvd_code}] ` + title_fmt;
        const title_short = (title_fmt.length > 80) ? title_fmt.slice(0, 78) + '...' : title_fmt;
        
        const year_el_style = (date_released_fmt !== 'null') ? '' : 'display: none;';
        
        const is_new = this._second_from_now(this.date_added) < 60*60*24*7;

        // #endregion
    
        // #region - html --------------------------------------------------------------------------
        
        this.shadowRoot.innerHTML = /* html */`
        
            <div class="${this.card_class}">

                <!-- image -->
                <a class="thumb-container" href="/pages/video/page.html?hash=${this.video_hash}">
                    <div class="spinner loader-2"></div>
                    <img class="thumbnail" src="" alt="">
                    <img class="teaser-thumbs" alt="">
                    <video class="teaser-video" preload="none" muted loop autoplay></video>
                    <div class="stats">
                        <div class="collection-container">
                            <div title="collection" class="collection">${this.collection}</div>
                            <div title="added in last week" class="is-new-indicator"
                                style="display: ${is_new ? "block;" : "none;"}"
                            >NEW</div>
                        </div>
                        <div class="top-right">
                            <div class="resolution" title="vertical resolution">
                                ${this.resolution}p
                            </div>
                            <div class="bitrate" title="bitrate mb/s">
                                ${Math.round(this.bitrate/100)/10}mb
                            </div>
                            <div class="fps" style="display: none;">${this.fps}</div>
                        </div>
                        <div class="duration">${this.duration}</div>
                    </div>
                </a>

                <!-- card info -->
                <div class="card-info-container">
                    <div class="details-bar">
                        <div class="left-side">
                            <span title="view time" class="viewtime">vt unknown</span>
                            <span class="likes-span">
                                <div class="likes">-1</div>
                                <svg width="32px" height="32px" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M1.24264 8.24264L8 15L14.7574 8.24264C15.553 7.44699 16 6.36786 16 5.24264V5.05234C16 2.8143 14.1857 1 11.9477 1C10.7166 1 9.55233 1.55959 8.78331 2.52086L8 3.5L7.21669 2.52086C6.44767 1.55959 5.28338 1 4.05234 1C1.8143 1 0 2.8143 0 5.05234V5.24264C0 6.36786 0.44699 7.44699 1.24264 8.24264Z" fill="#000000"/>
                                </svg>
                            </span>
                            <span title="rating" class="rating">
                                B+
                            </span>
                            <span title="subtitles available" class="has-subs" style="display: none">subs</span>
                        </div>
                        <div title="time ago added">
                            ${this.format_date_added(this.date_added)} ago
                        </div>
                    </div>
                    <div class="title-bar">
                        <button title="toggle favourite" class="is-fav-button">
                            <svg class="off" width="32px" height="32px" viewBox="-4 0 30 30" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:sketch="http://www.bohemiancoding.com/sketch/ns">
                                <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" sketch:type="MSPage"><g id="Icon-Set" sketch:type="MSLayerGroup" transform="translate(-417.000000, -151.000000)" fill="#000000">
                                    <path d="M437,177 C437,178.104 436.104,179 435,179 L428,172 L421,179 C419.896,179 419,178.104 419,177 L419,155 C419,153.896 419.896,153 421,153 L435,153 C436.104,153 437,153.896 437,155 L437,177 L437,177 Z M435,151 L421,151 C418.791,151 417,152.791 417,155 L417,177 C417,179.209 418.791,181 421,181 L428,174 L435,181 C437.209,181 439,179.209 439,177 L439,155 C439,152.791 437.209,151 435,151 L435,151 Z" id="bookmark" sketch:type="MSShapeGroup"></path>
                                </g></g>
                            </svg>
                            <svg class="on" width="32px" height="32px" viewBox="-4 0 30 30" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:sketch="http://www.bohemiancoding.com/sketch/ns">
                                <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" sketch:type="MSPage"><g id="Icon-Set-Filled" sketch:type="MSLayerGroup" transform="translate(-419.000000, -153.000000)" fill="#000000">
                                    <path d="M437,153 L423,153 C420.791,153 419,154.791 419,157 L419,179 C419,181.209 420.791,183 423,183 L430,176 L437,183 C439.209,183 441,181.209 441,179 L441,157 C441,154.791 439.209,153 437,153" id="bookmark" sketch:type="MSShapeGroup"></path>
                                </g></g>
                            </svg>

                        </button>
                        <a class="title" href="/pages/video/page.html?hash=${this.video_hash}">
                            <h2 title="${title_fmt}">${title_short}</h2>
                        </a>
                    </div>
                    <div class="studio-actors-container">
                        <div class="year-studio-bar">
                            <div title="date released" class="year" style="${year_el_style};">
                                ${date_released_fmt}
                            </div>
                            <div title="studio" class="studios-bar">
                                ${studios_html}
                            </div>
                        </div>
                        <div class="actors-bar">
                            ${actors_html}
                        </div>
                    </div>
                    <div class="tags-bar">
                        ${tags_html}
                    </div>
                </div>

            </div>
            `;


        // #endregion
        
        
        this.shadowRoot.innerHTML += this.getCSS();

    }

    
    // #region - HELPERS -----------------------------------------------------------------------------------------------

    format_date_added(date_added) {
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

    /* configure_teaser_thumb_spritesheet */
    configure_teaser_thumb_spritesheet(spritesheet_src, thumbnail_container, parent_container, loaded_callback=null) {
    
        const vtt_src = spritesheet_src.replace('.jpg', '.vtt');
        
        // First, load and parse the VTT file to get the sprite information
        fetch(vtt_src)
            .then(response => response.text())
            .then(vttText => {
                // console.log('got vtt text:', vttText);

                // Parse the VTT file to extract sprite coordinates
                const sprites = this.parseVTT(vttText);
                if (sprites.length === 0) {
                    throw new Error(`No sprites parsed from vtt file: ${vtt_src}`);
                };
                
                // Set up the spritesheet as the background for the thumbnail container
                
                thumbnail_container.style.backgroundImage = `url("${spritesheet_src}")`;
                thumbnail_container.style.backgroundRepeat = 'no-repeat';
                
                // load image to get spritesheet height
                const img = new Image();
                img.src = spritesheet_src;

                img.onload = () => {
                    const thumbAspectRatio = sprites[0].w / sprites[0].h;
                    const thumbContainerHeight = parent_container.clientHeight; // parents height because of possible display: none;
                    thumbnail_container.style.width = (thumbAspectRatio * thumbContainerHeight) + 'px';

                    // determine background image scale factor
                    const scaleFactor = (thumbContainerHeight / sprites[0].h);
                    thumbnail_container.style.backgroundSize = (img.naturalWidth * scaleFactor) + 'px ' + (img.naturalHeight * scaleFactor) + 'px';

                    // Calculate how many thumbnails we have
                    const thumbCount = sprites.length;
                    
                    // Handle mouse movement to update the thumbnail
                    parent_container.addEventListener('mousemove', (e) => {
                        // Calculate the percentage of mouse position within the parent container
                        const rect = parent_container.getBoundingClientRect();
                        const xPos = e.clientX - rect.left;
                        
                        const perc = Math.max(0, Math.min(1, xPos / rect.width));
                        const thumbIndex = Math.floor(perc * (thumbCount));
                        
                        const sprite = sprites[thumbIndex];
                        thumbnail_container.style.backgroundPosition = `-${sprite.x*scaleFactor}px -${sprite.y*scaleFactor}px`;
                    });
                    
                    if (loaded_callback) {
                        loaded_callback();
                    }
                }
            })
            .catch(error => {
                console.warn('Error loading thumbnails:', error);
            });
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
    

    format_seconds(seconds) {
        if (seconds === null || seconds === 0) return '';
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor( (seconds-hours*3600) / 60 );
        const secs = Math.floor( seconds - hours*3600 - mins*60 );
        if (hours > 0) {        return `${hours}h ${mins}m ${secs}s`;
        } else if (mins > 0) {  return `${mins}m ${secs}s`;
        } else {                return `${secs}s`;
        }
    }

    filter_tags(tags, max_chars) {
        const initial = [];
        let i = 0;
        let cumu = 0;
        while (i < tags.length && cumu + tags[i].length < max_chars) {
            initial.push(tags[i]);
            cumu += tags[i].length;
            i++;
        }
        const remaining = tags.slice(i);
        return [initial, remaining];
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    _second_from_now(date) {
        return (Date.now() - Date.parse(date)) / 1000;
    }
    

    _get_tag_color(tag_str) {
        if (tag_str.includes(": ")) {
            const pref = tag_str.split(": ")[0]
            switch (pref) {
                case "character":
                    return "color: #bbb !important; background: #1e3259;"
                case "source":
                    return "color: #bbb !important; background: #11975a58;"
            }
        }
        return ""
    }
    
    // #endregion
    
    // #region - css -------------------------------------------------------------------------------

    getCSS() {
        return /* html */`

            <!-- styles --------------------------------------------------------------------------->
            <style>
                
                /* card */
                .card {
                    border: 1px solid #88888819;
                    width: ${this.card_width};
                    padding: 0;
                    border-radius: 0.5rem;
                    outline: 0.5px solid #4441;
                    background: black;
                    display: block;
                    cursor: default;
                }
                .card.highlighted {
                    box-shadow: 0 0 10px yellow;
                }

                /* - THUMBNAIL HOVER ---------------------------------------- */
                a.thumb-container:hover img.thumbnail {
                    display: none;
                }
                a.thumb-container:hover .teaser-media.loaded {
                    display: block;
                }

                .spinner {
                    visibility: hidden;
                }
                a.thumb-container:hover .spinner {
                    visibility: visible;
                }
                
                /* - IMAGE PART --------------------------------------------- */
                a.thumb-container {
                    position: relative;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: #111;
                    border-radius: 5px;
                    font-size: 0.8rem;
                    width: 100%;
                    aspect-ratio: ${this.aspect_ratio};
                    height: auto;
                    object-fit: contain;
                    overflow: hidden;
                    user-select: none;
                    -webkit-user-drag: none;

                    * { box-sizing: border-box; }
                    
                    img.thumbnail {
                        height: 100%;
                        width: 100%;
                        object-fit: cover;
                    }
                    img.teaser-thumbs {
                        height: 100%;
                        width: 100%;
                        object-fit: cover;
                        display: none;
                    }
                    video {
                        height: 100%;
                        width: 100%;
                        /* object-fit: contain; */
                        object-fit: cover;
                        display: none;
                    }
                    div {
                        position: absolute;
                        padding: 0 2px;
                    }
                    .stats {
                        right: 0;
                        top: 0;
                        height: 100%;
                        width: 100%;
                        gap: 2px;
                    }
                    .stats > div {
                        width: fit-content;
                    }

                    .collection-container {
                        position: absolute;
                        top: 4px;
                        left: 7px;
                        display: flex;
                        gap: 3px;
                        width: fit-content;
                    }
                    .collection {
                        position: relative;
                        font-family: "Exo 2";
                        font-weight: 500;
                        font-size: 13px;
                        padding: 0 5px 1.5px 5px;
                        color: #fffd;
                        border: 1.8px solid #fffd;
                        border-radius: 7px;
                        background: #000b;
                    }
                    .collection:hover { opacity: 0.8; }
                    .collection:active { opacity: 1.0; }

                    .is-new-indicator {
                        display: none;
                        position: relative;
                        font-family: "Exo 2";
                        font-weight: 500;
                        font-size: 11px;
                        padding: 2px 5px 0px 5px;
                        color: rgb(255, 27, 27);
                        border: 1.8px solid rgb(255, 32, 32);
                        border-radius: 7px;
                        background: #000b;
                    }

                    .top-right {
                        top: 3px;
                        right: 4px;
                        display: flex;
                        justify-content: flex-start;
                        display: flex;
                        gap: 3px;
                    }
                    .top-right div {
                        position: relative;
                    }
                    .duration {
                        background: #0009;
                        right: 4px;
                        bottom: 4px;
                    }
                    
                    .resolution, .fps, .bitrate, .duration {
                        background: #0009;
                        padding: 1px 4px 0px 4px;
                        color: white;
                        border-radius: 5px;
                        font-size: 0.78rem;
                    }
                }

                /* - INFO PART ---------------------------------------------- */
                .card-info-container {
                    /* padding: 0.25 2rem !important; */ /* does fuck all */
                    display: block;
                    box-sizing: border-box;
                    min-height: 8rem;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }

                .details-bar, .title-bar, .year-studio-bar, .studios-bar, .actors-bar, .tags-bar, .left-side {
                    display: flex;
                    align-items: center;
                }

                /* details bar */
                .details-bar {
                    font-size: 0.71rem;
                    justify-content: space-between;
                    color: #999;
                    padding: 0.25rem 0.7rem;
                }
                .left-side {
                    gap: 0.65rem;
                }
                .likes-span {
                    display: none;
                    align-items: center;
                    gap: 1.5px;
                    text-align: center;
                }
                .amount {
                    /* margin-bottom: 2px; */
                    background: purple;
                }
                .likes-span svg {
                    height: 10px;
                    width: auto;
                }
                .likes-span svg path {
                    fill: rgba(255, 0, 0, 0.774);
                }
                .rating {
                    font-family: 'Jaro';
                    font-size: 0.8rem;
                    color: #bb9;
                }
                .has-subs {
                    border: 1px solid grey;
                    border-radius: 4px;
                    padding: 0.5px 2px;
                    padding-top: 0;
                }

                /* title bar */
                .title-bar {
                    padding: 0 4px;
                    align-items: start;

                    h2 {
                        font-family: "Quicksand";
                        color: #eee;
                        font-size: 1.3rem;
                        letter-spacing: -0.6px;
                        font-weight: 100px;
                        margin: 0;
                        text-align: left;
                    }
                }

                /* is-favourite button */
                .is-fav-button {
                    all: unset;
                    height: 1.3rem;
                    min-width: 1.2rem;
                    margin: 0.1rem 0.6rem;
                    padding: 0.2rem;
                    cursor: pointer;
                }
                .is-fav-button svg {
                    display: none;
                    height: 100%;
                    width: auto;
                }
                .is-fav-button .off path { fill: rgba(245, 245, 220, 0.801); }
                .is-fav-button .on path  { fill: rgba(236, 195, 59, 0.801); }
                
                .is-fav-button.loaded.is-fav       svg.on  { display: block; }
                .is-fav-button.loaded:not(.is-fav) svg.off { display: block; }
                .is-fav-button:active svg {
                    opacity: 0.8;
                }
                
                /* studio-actors container */
                .studio-actors-container {
                    margin: 0.1rem 1rem;
                    margin-left: 2rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.2rem;
                }

                .year-studio-bar {
                    gap: 0.6rem;
                    color: #bbb;
                    margin-left: 1.2rem;
                }

                .year {
                    font-weight: bold;
                    margin-top: 2px;
                    margin-right: 0.2rem;
                }
                
                .studios-bar, .actors-bar {
                    font-family: 'Inria Serif';
                    font-weight: bold;
                    gap: 0.3rem;
                    color: #888;
                    font-size: 1rem;
                    /* font-weight: 400; */
                }
                .studios-bar {
                    font-weight: 500;
                    color: #777;
                    font-family: "Inter";
                }
                .actors-bar {
                    flex-wrap: wrap;
                    margin-bottom: 5px;
                }
                .actors-bar a {
                    text-wrap: nowrap;
                }

                /* separator */
                .studios-bar span,
                .actors-bar span {
                    height: 4px;
                    width: 4px;
                    background: #888;
                    margin: 0 2px;
                    transform: rotate(45deg);
                    user-select: none;
                    background: #fa09;
                }

                .tags-bar {
                    margin: 0.5rem 0.5rem;
                    margin-top: auto;
                    justify-content: flex-end;
                    gap: 3px;
                    flex-wrap: wrap;
                }
                .tags-bar a {
                    text-wrap: nowrap;
                }

                /* a tags */
                .card-info-container a {
                    text-decoration: none;
                    color: #aaa;
                }
                .card-info-container a:hover {
                    text-decoration: underline;
                }
                .card-info-container .title-bar a {
                    text-decoration: none;
                }
                .tags-bar a {
                    font-family: sans-serif;
                    font-size: 0.67rem;
                    font-weight: Bold;
                    letter-spacing: 0px;
                    background: #151515;
                    border-radius: 5px;
                    padding: 1.5px 6px;
                    color: #888 !important;
                }
                .tags-bar a:hover {
                    text-decoration: none !important;
                }
                


                /* - LOADERS ------------------------------------------------ */
                /* .loader-1 {
                    width: 1.6rem;
                    height: 1.6rem;
                    border-radius: 50%;
                    display: inline-block;
                    border-top: 3px solid #FFF;
                    border-right: 3px solid transparent;
                    box-sizing: border-box;
                    animation: rotation-1 1.2s linear infinite;
                }
                @keyframes rotation-1 {
                    0% {    transform: rotate(0deg); }
                    100% {  transform: rotate(360deg); }
                } */

                .loader-2 {
                    width:  27px;
                    height: 27px;
                    border-radius: 50%;
                    display: inline-block;
                    position: absolute;
                    top: calc(50% - 13px);
                    left: calc(50% - 13px);
                    background: linear-gradient(0deg, rgba(255, 61, 0, 0.2) 33%, #ff3d00 100%);
                    box-sizing: border-box;
                    animation: rotation-2 1s linear infinite;
                    transform: scale(50%);
                }
                .loader-2::after {
                    content: '';  
                    box-sizing: border-box;
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    background: #181616;
                }
                @keyframes rotation-2 {
                    0% { transform: rotate(0deg) }
                    100% { transform: rotate(360deg)}
                }
                
            </style>

        `;
    }
    
    // #endregion
    
    
}
customElements.define('search-result-card-default', MyCard);


