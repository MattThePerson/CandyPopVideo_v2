
const searchInput = document.getElementById("nav-bar-search-input");
const headerSearchButton = document.getElementById("nav-bar-search-button");
const urlParams = new URLSearchParams(window.location.search);

/* searchInput.addEventListener("keydown", e => {
    if (e.key === 'Enter') {
        console.log(e.target.value);
    }
});
 */

headerSearchButton.addEventListener("click", e => {
    value = searchInput.value;
    if (value != "") {
        const urlParams = new URLSearchParams({'query' : value});
        url = "searchPage.html?" + urlParams.toString();
        window.location.href = url;
    } else {
        console.log("No string given to input");
    }
});

/* 
// save page scroll
window.addEventListener('beforeunload', function() {
    localStorage.setItem('scrollPosition', window.scrollY);
});

// Restore the scroll position after the page loads
window.addEventListener('load', function() {
    setTimeout(function() {
        const scrollPosition = localStorage.getItem('scrollPosition');
        if (scrollPosition) {
            window.scrollTo(0, parseInt(scrollPosition, 10));
        }
    }, 100);
});
 */


/* API FUNCTIONS */

const flask_api_url = "http://127.0.0.1:5011/";

function makeApiRequestGET(request, args, callback) {
    let api_call = request;
    for (let arg of args) {
        api_call = api_call + "/" + arg;
    }
    fetch(flask_api_url + api_call)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            /* console.log(data); */
            //media_path = 'file:\\\\\\' + data.media_path;
            //favourites_ids = data.favourites_ids;
            //collections = data.collections;
            callback(data.main)
        })
        .catch(error => {
            console.error('Fetch error:', error);
    });
}


function makeApiRequestGET_JSON(request, data, callback) {
    const url = new URL(flask_api_url + request);
    Object.keys(data).forEach(key => url.searchParams.append(key, String(data[key])));
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            /* console.log(data); */
            media_path = 'file:\\\\\\' + data.media_path;
            favourites_ids = data.favourites_ids;
            callback(data.main)
        })
        .catch(error => {
            console.error('Fetch error:', error);
    });
}


/* GLOBAL FUNCTIONS */

function GLOBAL_video_is_favourite(hash, callback) {
    //console.log("Checking if video is favourite: " + hash);
    makeApiRequestGET('is-favourite', [hash], arg => {
        if (arg && arg.is_favourite) {
            callback();
        }
    });
}


/* COOKIE FUNCTIONS */

function setCookie(name, value) {
    document.cookie = name + "=" + (value || "") + "; path=/"; // 'path=/' ensures cookie is accessible on all pages
}

function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';'); // Get all cookies
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length); // Remove leading spaces
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length); // Check if cookie name matches
    }
    return null;
}

function eraseCookie(name) {
    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

function eraseAllCookies() {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i];
        let eqPos = cookie.indexOf("=");
        let name = eqPos > -1 ? cookie.substring(0, eqPos) : cookie;
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
    }
}

/* Event listener for reloading backend */


document.getElementById("reload-backend-button")?.addEventListener('click', e => {
    e.preventDefault();
    console.log('Clicked!');
    makeApiRequestGET('reload-backend', [], () => {});
});

