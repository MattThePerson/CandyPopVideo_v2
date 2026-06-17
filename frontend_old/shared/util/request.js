



/* API FUNCTIONS */

/* get request */
export function makeApiRequestGET(request, args, callback) {

    let api_call = request;
    for (let arg of args) {
        api_call = api_call + '/' + arg;
    }

    fetch(api_call)
        .then(response => {
            if (!response.ok) {
                throw new Error(`(${request}) Network response: ${response.status}`);
            }
            // console.log(`(${request}) 1st then`);
            try {
                return response.json();
            } catch (error) {
                return response.text();
            }
        })
        .then(data => {
            // console.log(`(${request}) 2nd then`);
            try {
                callback(data)
            } catch (error) {
                throw new Error(`Exception during callback for '${request}'`)
            }
        })
        .catch(error => {
            // console.error(error);
    });
    
}


/* post json object */
export function makeApiRequestPOST_JSON(request, data, callback) {
    
    const options = {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data),
    }
    
    fetch(request, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`(${request}) Network response: ${response.status}`);
            }
            // console.log(response);
            return response.json();
        })
        .then(data => {
            try {
                callback(data)
            } catch (error) {
                console.error(`Callback error (${request}):`, error);
            }
        })
        .catch(error => {
            console.error(error);
    });

}

/* post request */
export function makeApiRequestPOST(request, args, callback) {
    
    const options = {
        method: "POST"
    }

    let api_call = request;
    for (let arg of args) {
        api_call = api_call + '/' + arg;
    }

    fetch(api_call, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`(${request}) Network response: ${response.status}`);
            }
            // console.log(response);
            return response.json();
        })
        .then(data => {
            try {
                callback(data)
            } catch (error) {
                console.error(`Callback error (${request}):`, error);
            }
        })
        .catch(error => {
            console.error(error);
    });

}



/* COOKIE FUNCTIONS */

export function setCookie(name, value) {
    document.cookie = name + "=" + (value || "") + "; path=/"; // 'path=/' ensures cookie is accessible on all pages
}

export function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';'); // Get all cookies
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length); // Remove leading spaces
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length); // Check if cookie name matches
    }
    return null;
}

export function eraseCookie(name) {
    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

export function eraseAllCookies() {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i];
        let eqPos = cookie.indexOf("=");
        let name = eqPos > -1 ? cookie.substring(0, eqPos) : cookie;
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
    }
}


