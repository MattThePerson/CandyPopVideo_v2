


function addHtmlComponents() {
    adders = document.getElementsByClassName("html-component-injector");
    for (let i = adders.length-1; i >= 0; i--) {
        element = adders[i];
        componentName = element.getAttribute("html-component");
        //console.log("Injecting HTML component: " + componentName);
        html = componentMethods[componentName]();
        if (html) {
            element.insertAdjacentHTML("afterend", html);
            element.remove();
        } else {
            console.log("ERROR: Unable to get html for component " + componentName);
        }
    }
}

componentMethods = {
    "header" : HeaderTemplate,
    "footer" : FooterTemplate
}

/* COMPONENT METHODS */

function HeaderTemplate() {
    return /* html */`
<header>
    <div class="logo-parent">
        <a href="index.html" class="logo">CandyPop</a>
    </div>
    <nav class="top-nav">
        <a href="pages/home/index.html" class="top-nav-item">HOME</a>
        <a href="pages/search/index.html" class="top-nav-item">SEARCH</a>
        <!-- <a href="../list/index.html?sortby=date-released-desc" class="top-nav-item">LIST PAGE</a> -->
        <a href="pages/catalogue/index.html" class="top-nav-item">CATALOGUE</a>
        <a href="pages/video/index.html" class="top-nav-item">RANDOM VIDEO</a>
        <!-- <a href="../spreadsheet/index.html" class="top-nav-item">SPREADSHEET</a> -->
        <!-- <a href="../gifs/index.html" class="top-nav-item">GIFS</a> -->
        <!-- <a href="../curatedCollections/index.html" class="top-nav-item">CURATED</a> -->
        <form class="search-bar-form" onSubmit="return false;">
            <input id="nav-bar-search-input" class="top-nav-item" type="search" placeholder="Search.." autocomplete="off">
            <button id="nav-bar-search-button" type="submit">
                <svg class="nav-bar-search-icon" width="20px" viewBox="0 0 24 24" fill="none" ><path d="M16.6725 16.6412L21 21M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
        </form>
        <a href="pages/dashboard/index.html" class="top-nav-item icon-nav-parent">
            <svg class="icon icon-construction" width="20px" viewBox="0 0 24 24">
                <path fill-rule="evenodd" clip-rule="evenodd" 
                d="M3.13861 8.5856C3.10395 8.79352 3.07799 8.98444 3.05852 9.15412C2.89911 9.20305 2.72733 9.2683 2.55279 9.35557C2.18416 9.53989 1.78511 9.83206 1.48045 10.2891C1.17162 10.7523 1 11.325 1 12C1 12.675 1.17162 13.2477 1.48045 13.7109C1.78511 14.1679 2.18416 14.4601 2.55279 14.6444C2.72733 14.7317 2.89911 14.7969 3.05852 14.8459C3.07798 15.0156 3.10395 15.2065 3.13861 15.4144C3.27452 16.2299 3.54822 17.3325 4.10557 18.4472C4.66489 19.5658 5.51956 20.7149 6.8203 21.5821C8.1273 22.4534 9.82502 23 12 23C14.175 23 15.8727 22.4534 17.1797 21.5821C18.4804 20.7149 19.3351 19.5658 19.8944 18.4472C20.4518 17.3325 20.7255 16.2299 20.8614 15.4144C20.896 15.2065 20.922 15.0156 20.9415 14.8459C21.1009 14.7969 21.2727 14.7317 21.4472 14.6444C21.8158 14.4601 22.2149 14.1679 22.5196 13.7109C22.8284 13.2477 23 12.675 23 12C23 11.325 22.8284 10.7523 22.5196 10.2891C22.2149 9.83206 21.8158 9.53989 21.4472 9.35557C21.2727 9.2683 21.1009 9.20305 20.9415 9.15412C20.922 8.98444 20.896 8.79352 20.8614 8.5856C20.7255 7.77011 20.4518 6.6675 19.8944 5.55278C19.3351 4.43416 18.4804 3.28511 17.1797 2.41795C15.8727 1.54662 14.175 1 12 1C9.82502 1 8.1273 1.54662 6.8203 2.41795C5.51957 3.28511 4.66489 4.43416 4.10558 5.55279C3.54822 6.6675 3.27452 7.77011 3.13861 8.5856ZM18.9025 15H5.09753C5.20639 15.692 5.43305 16.63 5.89443 17.5528C6.33511 18.4342 6.98044 19.2851 7.9297 19.9179C8.8727 20.5466 10.175 21 12 21C13.825 21 15.1273 20.5466 16.0703 19.9179C17.0196 19.2851 17.6649 18.4342 18.1056 17.5528C18.5669 16.63 18.7936 15.692 18.9025 15ZM18.9025 9H18C17.4477 9 17 9.44771 17 10C17 10.5523 17.4477 11 18 11H20C20.3084 11.012 20.6759 11.1291 20.8554 11.3984C20.9216 11.4977 21 11.675 21 12C21 12.325 20.9216 12.5023 20.8554 12.6016C20.6759 12.8709 20.3084 12.988 20 13H4C3.69155 12.988 3.32414 12.8709 3.14455 12.6016C3.07838 12.5023 3 12.325 3 12C3 11.675 3.07838 11.4977 3.14455 11.3984C3.32414 11.1291 3.69155 11.012 4 11H6C6.55228 11 7 10.5523 7 10C7 9.44771 6.55228 9 6 9H5.09753C5.20639 8.30804 5.43306 7.36996 5.89443 6.44721C6.33512 5.56584 6.98044 4.71489 7.92971 4.08205C8.24443 3.87224 8.59917 3.68195 9 3.52152V6C9 6.55228 9.44771 7 10 7C10.5523 7 11 6.55228 11 6V3.04872C11.3146 3.01691 11.6476 3 12 3C12.3524 3 12.6854 3.01691 13 3.04872V6C13 6.55228 13.4477 7 14 7C14.5523 7 15 6.55228 15 6V3.52152C15.4008 3.68195 15.7556 3.87224 16.0703 4.08205C17.0196 4.71489 17.6649 5.56584 18.1056 6.44721C18.5669 7.36996 18.7936 8.30804 18.9025 9Z"/>
            </svg>
        </a>
    </nav>
</header>

<style>
    header {
        background: var(--nav-dark);
        height: 60px;
        width: 100%;
        border-bottom: 1px solid var(--off-white);
        box-sizing: border-box;
        padding: 0 calc(2%);
        display: flex;
        justify-content: space-between;
        align-items: center;
        overflow: hidden;
    }

    .logo-parent {
        /* background: pink; */
        display: flex;
        flex-grow: 5;
    }

    .top-nav {
        /* background: green; */
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-grow: 0.25;
    }

    .logo {
        font-family: "Alba";
        font-size: 30px;
        letter-spacing: 1.5px;
        margin-right: 0.5em;
    }

    .top-nav-item {
        /* background: blue; */
        padding: 7px 7px;
        margin: 0 0.25em;
        font-family: "Exo 2";
        font-weight: 600;
        font-size: 18px;
        white-space: nowrap;
    }

    .search-bar-form {
        width: 225px;
        height: 30px;
        background: green;
        background: #fafafa;
        box-sizing: border-box;
        padding: 0 0.1em;
        border-radius: 12px;
        display: flex;
    }
    .search-bar-form input:focus {
        outline: None;
    }

    #nav-bar-search-input {
        width: 100%;
        background: None;
        color: #333;
        font-size: 16px;
        font-weight: 400;
        border: None;
        font-family: "Roboto Condensed";
    }
    #nav-bar-search-button {
        height: 100%;
        min-width: 20px;
        border: None;
        background: None;
        transform: translateX(-3px);
    }
    #nav-bar-search-button:hover {
        cursor: pointer;
    }
    #nav-bar-search-button:active {
        background: #0001;
    }

    /* HEADER LINK STYLING */

    header a {
        text-decoration: None;
        
    }
    header a:hover {
        color: var(--actor-rose);
    }
    header a:active {
        color: var(--active-rose);
    }

    .icon-construction {
        min-width: 28px;
    }
    .icon-construction path {
        fill: var(--off-white);
    }
    .icon-nav-parent:hover path {
        fill: var(--actor-rose);
    }
    .icon-nav-parent:active path {
        fill: var(--active-rose);
    }
</style>

    `
}

function FooterTemplate() {
    return /* html */`
<footer>
    <div>CopyLeft © 2069 CandyPop</div>
    <div>All rights are mine and yours</div>
</footer>
<style>
    footer {
        text-align: center;
        min-height: 30px;
        width: 100%;
        background: var(--nav-dark);
        box-sizing: border-box;
        padding: 2em;
        /* margin-top: 15em; */
    }
</style>
`}

addHtmlComponents();