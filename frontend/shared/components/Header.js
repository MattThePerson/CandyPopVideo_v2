
export function Header(){
    /* html */
    return `

<header>
    <nav>
        <span>
            <a id='logo' href="/"         class:active={$page.url.pathname === "/"}>
                <span id="logo">
                    <div>CandyPop</div>
                    <div>Video</div>
                </span>
            </a>

        </span>
        
        <span>
            <span class="page-links">
                <a class="page-link" href="/pages/home/page.html"      >home</a>
                <a class="page-link" href="/pages/search/page.html"    >search</a>
                <a class="page-link" href="/pages/catalogue/page.html" >catalogue</a>
                <a class="page-link" href="/pages/curated/page.html"   >curated</a>
            </span>

            <button id="random-video-button" class="icon-button">
                <a href="/pages/video/page.html">
                    <svg fill="#000000" width="32px" height="32px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                        <path d="M504.971 359.029c9.373 9.373 9.373 24.569 0 33.941l-80 79.984c-15.01 15.01-40.971 4.49-40.971-16.971V416h-58.785a12.004 12.004 0 0 1-8.773-3.812l-70.556-75.596 53.333-57.143L352 336h32v-39.981c0-21.438 25.943-31.998 40.971-16.971l80 79.981zM12 176h84l52.781 56.551 53.333-57.143-70.556-75.596A11.999 11.999 0 0 0 122.785 96H12c-6.627 0-12 5.373-12 12v56c0 6.627 5.373 12 12 12zm372 0v39.984c0 21.46 25.961 31.98 40.971 16.971l80-79.984c9.373-9.373 9.373-24.569 0-33.941l-80-79.981C409.943 24.021 384 34.582 384 56.019V96h-58.785a12.004 12.004 0 0 0-8.773 3.812L96 336H12c-6.627 0-12 5.373-12 12v56c0 6.627 5.373 12 12 12h110.785c3.326 0 6.503-1.381 8.773-3.812L352 176h32z"/>
                    </svg>
                </a>
            </button>
            
            <button id="search-button" class="icon-button" >
                <svg fill="#000000" width="32px" height="32px" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.027 9.92L16 13.95 14 16l-4.075-3.976A6.465 6.465 0 0 1 6.5 13C2.91 13 0 10.083 0 6.5 0 2.91 2.917 0 6.5 0 10.09 0 13 2.917 13 6.5a6.463 6.463 0 0 1-.973 3.42zM1.997 6.452c0 2.48 2.014 4.5 4.5 4.5 2.48 0 4.5-2.015 4.5-4.5 0-2.48-2.015-4.5-4.5-4.5-2.48 0-4.5 2.014-4.5 4.5z" fill-rule="evenodd"/>
                </svg>
            </button>

            <a class="dashboard-link" href="/pages/dashboard/page.html">dashboard</a>
        </span>
        
    </nav>
</header>

<script>
    /* make current page link active */
    document.querySelectorAll('nav a').forEach(a_el => {
        if (a_el.href.includes(document.location.pathname)) a_el.classList.add('active')
    })
</script>


<style>
    
    /* LOGO */
    #logo {
        span {
            display: flex;
            align-items: center;
            gap: 0.2rem;
        }
        
        div:nth-child(1) { /* CandyPop */
            font-family: 'Jaro';
            font-size: 1.7rem;
            color: #eee;
            transform: translateY(-2.5px);
        }
        div:nth-child(2) { /* Video */
            color: orange;
            font-family: sans-serif;
            font-weight: 600;
            font-size: 1.3rem;
        }
    }
    
    nav {
        display: flex;
        justify-content: space-between;
        padding: 0 2.5%;
        background: black;
        outline: 1px solid #fff3;
        
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
            padding: 0.4rem 0.5rem;
            font-size: 1.2rem;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            color: #d3d3d3;
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
            height: 100%;
            fill: #ccc;
        }
    }
    .icon-button:hover svg {
        fill: white;
    }

</style>

    `
}
