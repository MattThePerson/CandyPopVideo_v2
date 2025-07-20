
export function Header(){
    
    return /* html */`


<!-- script ----------------------------------------------------------------------------------------------------------->
<script>
    /* make current page link active */
    // document.querySelectorAll('nav a').forEach(a_el => {
    //     if (a_el.href.includes(document.location.pathname)) a_el.classList.add('active')
    // });

    $('nav a').each((_, el) => {
        if (el.href.includes(document.location.pathname)) {
            $(el).addClass('active');
        }
    });

    /* config menu */
    $('#config-menu-button').click(() => {
        $('.config-menu').toggleClass('hidden');
    });
    $(document).on('mousedown', (e) => {
        if ($(e.target).closest('#config-menu-button').length <= 0) {
            if ($(e.target).closest('.config-menu').length <= 0) {
                $('.config-menu').addClass('hidden');
            }
        }
    });

    /* use video teasers buttons */
    const useVideoTeasers = (localStorage.getItem('use_video_teasers') == 'true');
    if (useVideoTeasers) {
        $('#teaser-mode-video').addClass('selected');
    } else {
        $('#teaser-mode-image').addClass('selected');
    }
    $('#teaser-mode-video').on('click', () => {
        if (!useVideoTeasers) {
            localStorage.setItem('use_video_teasers', 'true');
            location.reload();
        }
    });
    $('#teaser-mode-image').on('click', () => {
        if (useVideoTeasers) {
            localStorage.setItem('use_video_teasers', 'false');
            location.reload();
        }
    });

    /* card size buttons */
    const cardSize = localStorage.getItem('card_size') || 'medium';
    const cardSizeSel = '#card-size-' + cardSize;
    $(cardSizeSel).addClass('selected');
    $('.card-size button').each((idx, button) => {
        button.onclick = () => {
            if (!$(button).hasClass('selected')) {
                const new_card_size = button.id.replace('card-size-', '');
                localStorage.setItem('card_size', new_card_size);
                location.reload();
            }
        }
    })
    

</script>


<!-- html ------------------------------------------------------------------------------------------------------------->
<header>
    <nav>

        <!-- logo -->
        <span>
            <a id='logo' href="/"         class:active={$page.url.pathname === "/"}>
                <span id="logo">
                    <div class="main">CandyPop</div>
                    <div class="secondary-text">Video</div>
                </span>
            </a>

        </span>
        
        <!-- page nav -->
        <span>
            <span class="page-links">
                <a class="page-link" href="/pages/home/page.html"        >home</a>
                <a class="page-link" href="/pages/search/page.html"      >search</a>
                <a class="page-link" href="/pages/search_new/page.html"  >search(new)</a>
                <a class="page-link" href="/pages/catalogue/page.html"   >catalogue</a>
                <a class="page-link" href="/pages/curated/page.html"     >curated</a>
            </span>

            <button id="random-video-button" class="icon-button">
                <a href="/pages/video_new/page.html">
                    <svg fill="#000000" width="32px" height="32px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                        <path d="M504.971 359.029c9.373 9.373 9.373 24.569 0 33.941l-80 79.984c-15.01 15.01-40.971 4.49-40.971-16.971V416h-58.785a12.004 12.004 0 0 1-8.773-3.812l-70.556-75.596 53.333-57.143L352 336h32v-39.981c0-21.438 25.943-31.998 40.971-16.971l80 79.981zM12 176h84l52.781 56.551 53.333-57.143-70.556-75.596A11.999 11.999 0 0 0 122.785 96H12c-6.627 0-12 5.373-12 12v56c0 6.627 5.373 12 12 12zm372 0v39.984c0 21.46 25.961 31.98 40.971 16.971l80-79.984c9.373-9.373 9.373-24.569 0-33.941l-80-79.981C409.943 24.021 384 34.582 384 56.019V96h-58.785a12.004 12.004 0 0 0-8.773 3.812L96 336H12c-6.627 0-12 5.373-12 12v56c0 6.627 5.373 12 12 12h110.785c3.326 0 6.503-1.381 8.773-3.812L352 176h32z"/>
                    </svg>
                </a>
            </button>
            
            <button id="header-search-button" class="icon-button" >
                <svg fill="#000000" width="32px" height="32px" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.027 9.92L16 13.95 14 16l-4.075-3.976A6.465 6.465 0 0 1 6.5 13C2.91 13 0 10.083 0 6.5 0 2.91 2.917 0 6.5 0 10.09 0 13 2.917 13 6.5a6.463 6.463 0 0 1-.973 3.42zM1.997 6.452c0 2.48 2.014 4.5 4.5 4.5 2.48 0 4.5-2.015 4.5-4.5 0-2.48-2.015-4.5-4.5-4.5-2.48 0-4.5 2.014-4.5 4.5z" fill-rule="evenodd"/>
                </svg>
            </button>

            <a class="dashboard-link" href="/pages/dashboard/page.html">dashboard</a>

            <!-- config menu -->
            <div class="config-menu-anchor">
                <button id="config-menu-button" class="icon-button" >
                    <svg fill="#000000" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 45.973 45.973" xml:space="preserve">
                        <g><g><path d="M43.454,18.443h-2.437c-0.453-1.766-1.16-3.42-2.082-4.933l1.752-1.756c0.473-0.473,0.733-1.104,0.733-1.774 c0-0.669-0.262-1.301-0.733-1.773l-2.92-2.917c-0.947-0.948-2.602-0.947-3.545-0.001l-1.826,1.815 C30.9,6.232,29.296,5.56,27.529,5.128V2.52c0-1.383-1.105-2.52-2.488-2.52h-4.128c-1.383,0-2.471,1.137-2.471,2.52v2.607 c-1.766,0.431-3.38,1.104-4.878,1.977l-1.825-1.815c-0.946-0.948-2.602-0.947-3.551-0.001L5.27,8.205 C4.802,8.672,4.535,9.318,4.535,9.978c0,0.669,0.259,1.299,0.733,1.772l1.752,1.76c-0.921,1.513-1.629,3.167-2.081,4.933H2.501 C1.117,18.443,0,19.555,0,20.935v4.125c0,1.384,1.117,2.471,2.501,2.471h2.438c0.452,1.766,1.159,3.43,2.079,4.943l-1.752,1.763 c-0.474,0.473-0.734,1.106-0.734,1.776s0.261,1.303,0.734,1.776l2.92,2.919c0.474,0.473,1.103,0.733,1.772,0.733 s1.299-0.261,1.773-0.733l1.833-1.816c1.498,0.873,3.112,1.545,4.878,1.978v2.604c0,1.383,1.088,2.498,2.471,2.498h4.128 c1.383,0,2.488-1.115,2.488-2.498v-2.605c1.767-0.432,3.371-1.104,4.869-1.977l1.817,1.812c0.474,0.475,1.104,0.735,1.775,0.735 c0.67,0,1.301-0.261,1.774-0.733l2.92-2.917c0.473-0.472,0.732-1.103,0.734-1.772c0-0.67-0.262-1.299-0.734-1.773l-1.75-1.77 c0.92-1.514,1.627-3.179,2.08-4.943h2.438c1.383,0,2.52-1.087,2.52-2.471v-4.125C45.973,19.555,44.837,18.443,43.454,18.443z M22.976,30.85c-4.378,0-7.928-3.517-7.928-7.852c0-4.338,3.55-7.85,7.928-7.85c4.379,0,7.931,3.512,7.931,7.85 C30.906,27.334,27.355,30.85,22.976,30.85z"/></g></g>
                    </svg>
                </button>
                
                <div class="config-menu hidden">
                    <section class="teaser-mode">
                        <h3>teaser mode</h3>
                        <div class="selector">
                            <button id="teaser-mode-image">image</button>
                            <button id="teaser-mode-video">video</button>
                        </div>
                    </section>
                    <section class="card-size">
                        <h3>card size</h3>
                        <div class="selector vertical">
                            <button id="card-size-small">small</button>
                            <button id="card-size-medium">medium</button>
                            <button id="card-size-large">large</button>
                        </div>
                    </section>
                    <section class="card-style">
                        <h3>card style</h3>
                        <div class="selector vertical">
                            <button id="card-style-default" class="selected">default</button>
                            <button id="card-style-fancy">fancy</button>
                            <button id="card-style-simple">simple</button>
                        </div>
                    </section>
                </div>
                
            </div>

        </span>
        
    </nav>
</header>

<!-- styles ----------------------------------------------------------------------------------------------------------->
<style>
    
    /* LOGO */
    #logo {
        padding: 0;
        
        span {
            display: flex;
            align-items: center;
            gap: 0.2rem;
        }
        
        .main { /* CandyPop */
            font-family: 'Jaro';
            font-size: 1.7rem;
            color: #eee;
            transform: translateY(-2.5px);
        }
        .secondary-text { /* Video */
            font-family: sans-serif;
            color: rgb(240, 102, 22);
            font-weight: 600;
            font-size: 1.4rem;
            letter-spacing: -0.5px;
        }
    }
    
    nav {
        display: flex;
        justify-content: space-between;
        padding: 0 2.5%;
        background: black;
        border: 1px solid #fff3;
        min-height: 3.1rem;
        
        span {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.3rem;
        }
    
        a {
            text-decoration: none;
            padding: 0.4rem 0.3rem;
        }
        
        /* page links */
        .page-links {
            transform: translateY(2px);
            display: flex;
            gap: 1px;
        }
        .page-link {
            font-family: 'Inter';
            font-weight: 500;
            padding: 0.4rem 0.5rem;
            font-size: 1.15rem;
            color: #ddd;
        }
        .page-link:hover {
            color: #eee;
            text-decoration: underline dotted grey;
        }
        .page-link.active {
            color: rgb(204, 105, 179);
        }
        
        
        .icon-button {
            padding: 0;
            border: none;
            background: none;
            height: 1.3rem;
            cursor: pointer;
            padding: 0 0.2rem;
        }
        
        /* dashboard link */
        .dashboard-link {
            background: rgb(1, 184, 184);
            color: black;
            font-family: Verdana, Geneva, Tahoma, sans-serif;
            font-weight: 600;
            letter-spacing: -0.8px;
            font-size: 1.0rem;
            border-radius: 5px;
            padding: 0.4rem 0.7rem;
            margin: 0 0.7rem;
        }
        .dashboard-link:hover {
            color: #eee;
        }
        .dashboard-link.active {
            background: rgb(204, 105, 179);
        }
    }

    /* Icon Buttons */
    .icon-button {
        svg {
            width: auto;
            height: 100%;
            fill: #ccc;
        }
    }
    .icon-button:hover svg {
        fill: white;
    }

    /* config menu stuff */
    #config-menu-button {
        margin-top: 2px;
        transform: none;
        transition: transform 0.4s ease-out;
    }
    #config-menu-button:hover {
        transform: rotate(45deg);
    }

    .config-menu-anchor {
        position: relative;
    }
    
    .config-menu {
        display: block;
        position: absolute;
        top: 35px; right: 15px;
        width: auto;
        height: auto;
        background: black;
        border: 1px solid #fff9;
        border-radius: 10px;
        padding: 0.7rem 0.8rem;
        z-index: 9999;
    }
    .config-menu.hidden {
        display: hidden;
    }

    .config-menu section {
        margin-bottom: 0.7rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .config-menu h3 {
        display: inline-block;
        white-space: nowrap;
        color: #aaa;
        margin-bottom: 0.6rem;
        margin-top: 0.2rem;
        align-self: flex-start;
    }

    .config-menu .selector {
        display: flex;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #aaa3;
    }

    .config-menu .selector.vertical {
        flex-direction: column;
        width: 8rem;
        gap: 2px;
    }
    
    .config-menu button {
        all: unset;
        font-family: sans-serif;
        font-size: 0.9rem;
        font-weight: bold;
        background: #ddd;
        color: #333;
        padding: 0.4rem 1rem;
        cursor: pointer;
        border: 0.5px solid black;
        user-select: none; /* prevent sect selection */
    }
    .config-menu button:active {
        opacity: 0.8;
    }
    .config-menu button.selected {
        background: orangered;
        color: white;
    }

</style>

    `
}
