
/* SearchResultCard */
export class MyCard extends HTMLElement {

    constructor() {
        super();
    }

    connectedCallback() {
        // console.log("Custom element added to page.");
        this.attachShadow({ mode: 'open' });
        this.render();
        this.addEventListeners();
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

    /* EVENT LISTENERS */

    addEventListeners() {
        const $shadow = $(this.shadowRoot);
        
        $shadow.find('.thumb-container').on('mouseenter', cont => {
            console.log('hovered');
        });

        /* click on collection */
        $shadow.find('.collection').click(event => {
            event.preventDefault();
            window.location.href = '/pages/search/page.html?collection=' + this.getAttribute('collection');
        })
    }
    
    /* RENDER */

    render() {

        let scene_title = this.getAttribute('scene_title');
        let performers_str = this.getAttribute('performers');
        let studio = this.getAttribute('studio');
        let line = this.getAttribute('line');
        let date_released = this.getAttribute('date_released');
        let scene_description = this.getAttribute('scene_description');
        let collection = this.getAttribute('collection');
        let jav_code = this.getAttribute('jav_code');

        let duration = this.getAttribute('duration');
        let resolution = this.getAttribute('resolution');
        let fps = this.getAttribute('fps');
        let bitrate = this.getAttribute('bitrate');
        
        let video_hash = this.getAttribute('hash');
        let date_added = this.getAttribute('date_added');
        let tags_str = this.getAttribute('tags');
        let filename = this.getAttribute('filename');

        duration = duration.startsWith("0:") ? duration.substring(2) : duration;

        let date_released_fmt = date_released.replace(/-/g, '.');

        // studios html
        const studios = [studio, line].filter(el => (el !== null && el !== 'null'));
        const studios_html = studios.map(x =>
            `<a href="/pages/search/page.html?studio=${x}">
                ${x}
            </a>`
        ).join('\n')
        
        // performers html
        const performers_html = performers_str.split(',').filter(x => x !== '').map(x =>
            `<a href="/pages/search/page.html?performer=${x}">
                ${x}
            </a>`
        ).join('\n')
        
        // tags html
        const tags_html = tags_str.split(',').filter(x => x !== '').map(x =>
            `<a href="/pages/search/page.html?include_terms=${x}">
                ${x}
            </a>`
        ).join('\n')
        
        
        /* attribute affected variables */
        const card_class = (this.getAttribute('highlighted')) ? "card highlighted" : "card";
        const card_width = this.getAttribute('width') || "24rem";

        
        this.shadowRoot.innerHTML = /* html */`
        
            <!-- html ----------------------------------------------------------------------------->
            <div class="${card_class}">

                <!-- image -->
                <a class="thumb-container" href="/pages/video/page.html?hash=${video_hash}">
                    <img class="thumbnail" src="/media/get/poster/${video_hash}?t=${Date.now()}" alt="">
                    <img class="teaser-thumbs" src="" alt="">
                    <video preload="none" muted loop></video>
                    <span class="loader-2"></span>
                    <div class="stats">
                        <div class="collection">${collection}</div>
                        <div class="top-right">
                            <div class="resolution">${resolution}p</div>
                            <div class="bitrate">${Math.round(bitrate/100)/10}mb</div>
                            <div class="fps" style="display: none;">${fps}</div>
                        </div>
                        <div class="duration">${duration}</div>
                    </div>
                </a>

                <!-- card info -->
                <div class="card-info-container">
                    <div class="details-bar">
                        <div class="left-side">
                            <span class="views">9 views</span>
                            <span class="likes">3 likes</span>
                        </div>
                        <div>${this.format_date_added(date_added)} ago</div>
                    </div>
                    <div class="title-bar">
                        <button class="is-fav-button"></button>
                        <a href="">
                            <h2>${scene_title}</h2>
                        </a>
                    </div>
                    <div class="studio-actors-container">
                        <div class="year-studio-bar">
                            <div class="year">${date_released_fmt}</div>
                            <div class="studios-bar">
                                ${studios_html}
                            </div>
                        </div>
                        <div class="actors-bar">
                            ${performers_html}
                        </div>
                    </div>
                    <div class="tags-bar">
                        ${tags_html}
                    </div>
                </div>

            </div>

            <!-- styles --------------------------------------------------------------------------->
            <style>
                
                /* card */
                .card {
                    border: 1px solid #88888819;
                    width: ${card_width};
                    padding: 0;
                    border-radius: 0.5rem;
                    outline: 0.5px solid #4441;
                    background: black;
                    display: block;
                }
                .card.highlighted {
                    box-shadow: 0 0 10px yellow;
                }

                /* - IMAGE PART --------------------------------------------- */
                a.thumb-container:hover .thumbnail {
                    display: none;
                }
                
                a.thumb-container {
                    position: relative;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: #111;
                    border-radius: 5px;
                    font-size: 0.8rem;
                    width: 100%;
                    aspect-ratio: 16/9;
                    height: auto;
                    object-fit: contain;
                    overflow: hidden;

                    img.thumbnail {
                        height: 100%;
                        display: block;
                    }
                    video {
                        display: none;
                        height: 100%;
                        object-fit: contain;
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

                    .collection {
                        position: relative;
                        top: 4px;
                        left: 7px;
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
                    height: 8rem;
                    display: flex;
                    flex-direction: column;
                }

                .details-bar, .title-bar, .year-studio-bar, .studios-bar, .actors-bar, .tags-bar, .left-side {
                    display: flex;
                    align-items: center;
                }

                .details-bar {
                    font-size: 0.71rem;
                    justify-content: space-between;
                    color: #999;
                    padding: 0.25rem 0.7rem;

                    .left-side {
                        gap: 0.5rem;
                    }
                }

                .title-bar {
                    padding: 0 1rem;

                    .is-fav-button {
                        height: 1.3rem;
                        width: 1rem;;
                        background: rgba(238, 232, 170, 0.671);
                        border-radius: 10px;
                    }
                    h2 {
                        font-family: "Quicksand";
                        color: #eee;
                        font-size: 1.3rem;
                        letter-spacing: -0.6px;
                        font-weight: 100px;
                        margin: 0 0.6rem;
                        text-align: left;
                    }
                }

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
                }
                
                .studios-bar, .actors-bar {
                    gap: 0.3rem;
                    color: #888;
                    font-size: 1rem;
                    font-family: "Inter";
                    font-weight: 400;
                }
                .studios-bar {
                    font-weight: 500;
                    color: #777;
                }

                /* add | between performers/studios */
                .actors-bar > *:not(:last-child)::after,
                .studios-bar > *:not(:last-child)::after {
                    content: '|';
                    font-size: 0.8rem;
                }

                .tags-bar {
                    margin: 0.5rem 0.5rem;
                    margin-top: auto;
                    justify-content: flex-end;
                    gap: 3px;
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
                .loader-1 {
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
                }

                .loader-2 {
                    width: 27px;
                    height: 27px;
                    border-radius: 50%;
                    display: inline-block;
                    position: relative;
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
    
    /* HELPERS */

    format_date_added(date_added) {
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
}
customElements.define('search-result-card-default', MyCard);


