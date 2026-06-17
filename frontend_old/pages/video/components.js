

/**
 * 
 * @param {string} name 
 * @returns {[HTMLDivElement, Function]}
 */
export function get_actor_card(name) {
    const host = document.createElement('div');
    const shadow = host.attachShadow({ mode: 'open' });
    
    shadow.innerHTML = /* html */`
        <a class="actor-card" href="/pages/search/page.html?actor=${name}">
            <div class="pic-container">
                <img src="" alt="" class="pic">
                <svg fill="#000000" width="64px" height="64px" viewBox="0 0 512 512" id="_x30_1" version="1.1" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                    <g>
                        <ellipse cx="256" cy="130" rx="110" ry="130"/>
                        <path d="M36,478.191C36,390.825,134.497,320,256,320s220,70.825,220,158.191v0C476,496.863,460.863,512,442.192,512H69.808   C51.137,512,36,496.863,36,478.191L36,478.191z"/>
                    </g>
                </svg>
            </div>
            <div class="info">
                <div class="name">${name}</div>
                <div class="video-count">? videos</div>
                <div title="age in this scene" class="age-its">&#8203;</div>
            </div>

            <style>
                .actor-card {
                    display: flex;
                    align-items: center;
                    height: fit-content;
                    background: black;
                    text-decoration: none;
                    border-radius: 3rem;
                    border: 1px solid #fff3;
                }
                /* profile pic */
                .pic-container {
                    --size: 4.5rem;
                    width: var(--size);
                    height: var(--size);
                    min-width: var(--size);
                    background: #555;
                    overflow: hidden;
                    border-radius: 50%;
                }
                .pic-container svg {
                    width: 100%;
                    height: 90%;
                    transform: translateY(-0.6rem);
                    fill: #111;
                }
                .pic-container img {
                    width: 100%;
                    height: auto;
                    transform: scale(200%) translateY(-5%);
                    transform-origin: top center;
                }
                /* info */
                .info {
                    min-width: 5rem;
                    padding: 4px;
                    padding: bottom: 8px;
                    padding-right: 1.5rem;
                    font-family: "Nunito";
                    font-size: 14px;
                    color: #999;
                    text-wrap: nowrap;
                }
                .name {
                    font-size: 16px;
                    color: #eee;
                }
                .info > div:not(.name) {
                    margin-left: 0.5rem;
                }
                /* hover */
                .actor-card:hover { box-shadow: inset 0 0 5px #fff4; }
                .actor-card:hover .pic-container { outline: 1px solid #fff5; }
            </style>
        </a>
    `;

    const callback = ({video_count, age_its, profile_pic, aka=null}) => {
        const $shadow = $(shadow);
        if (age_its) {
            $shadow.find('.age-its').text(age_its + ' y/o ITS');
        }
        if (aka) {
            $shadow.find('.name').attr('title', 'aka: '+ aka);
        }

        /* add profile pic */
        if (profile_pic) {
            $shadow.find('.pic-container img').attr('src', profile_pic);
            $shadow.find('.pic-container svg').hide();
        }
        
        /* get video count (TEMP SOLUTION) */
        $.get('/api/get/actor-video-count/'+name, (data, status) => {
            if (status === 'success') {
                $shadow.find('.video-count').text(data.video_count + ' videos');
            }
        });
        
    }

    return [
        host,
        callback,
    ];
}
