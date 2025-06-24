

function add_year_separator(container) {
    const results = container.querySelectorAll('.video-result-item');
    let currentYear = getYear(results[0])
    if (currentYear === '') return;
    let bins = [];
    let count = 0;
    let add_i = 0;
    results.forEach((res, i) => {
        let year = getYear(res);
        if (year == currentYear) {
            count++;
        } else {
            let value = currentYear + ' (' + count + ' videos)';
            bins.push([add_i, value]);
            currentYear = year;
            add_i = i;
            count = 1;
        }
    });
    let value = currentYear + ' (' + count + ' videos)';
    bins.push([add_i, value]);

    const separatorTemplate = document.getElementById('separator-template');
    for (let bin of bins) {
        let i = bin[0];
        let value = bin[1];
        console.log(i, value);
        const res = results[i];
        const template = separatorTemplate.content.cloneNode(true);
        const separator = template.querySelector('.separator');
        separator.querySelector('.value').innerText = value;
        container.insertBefore(template, res);
    }
}

function getYear(item) {
    let year = item.querySelector('.year').innerText;
    return year.split('-')[0]
}

function add_movie_separator(container) {
    const results = container.querySelectorAll('.video-result-item');
    let currentMovie = getMovie(results[0]);
    let bins = [];
    let count = 1;
    let add_i = 0;
    results.forEach((res, i) => {
        let movie = getMovie(res);
        if (movie == currentMovie) {
            count++;
        } else if (count > 0) {
            bins.push([add_i, currentMovie]);
            console.log(bins);
            currentMovie = movie;
            add_i = i;
            count = 1;
        }
    });
    bins.push([add_i, currentMovie]);

    const separatorTemplate = document.getElementById('separator-template');
    for (let bin of bins) {
        let i = bin[0];
        let value = bin[1];
        console.log(i, value);
        const res = results[i];
        const template = separatorTemplate.content.cloneNode(true);
        const separator = template.querySelector('.separator');
        separator.querySelector('.value').innerText = value;
        container.insertBefore(template, res);
    }
}

function getMovie(item) {
    return item.querySelector('.title-container h2').innerText.split(' - ')[0];
}

function add_studio_separator(container) {
    const results = container.querySelectorAll('.video-result-item');
    let holdValue = get_studio(results[0]);
    if (holdValue === '') return;
    let bins = [];
    let count = 0;
    let add_i = 0;
    results.forEach((res, i) => {
        let current = get_studio(res);
        if (current == holdValue) {
            count++;
        } else {
            let value = holdValue + ' (' + count + ' videos)';
            bins.push([add_i, value]);
            holdValue = current;
            add_i = i;
            count = 1;
        }
    });
    let value = holdValue + ' (' + count + ' videos)';
    bins.push([add_i, value]);

    const separatorTemplate = document.getElementById('separator-template');
    for (let bin of bins) {
        let i = bin[0];
        let value = bin[1];
        console.log(i, value);
        const res = results[i];
        const template = separatorTemplate.content.cloneNode(true);
        const separator = template.querySelector('.separator');
        separator.querySelector('.value').innerText = value;
        container.insertBefore(template, res);
    }
}
function get_studio(item) {
    let value = item.querySelector('.studio').innerText;
    return value;
}

/* ADD SEPARATORS */

if (urlParams.get('sort-by') && urlParams.get('sort-by').includes('date-released')) {
    console.log('Adding year separator');
    // check if video results loaded
    const videoResultsCheck = setInterval(() => {
        try {
            if (videoResultsContainer.querySelectorAll('.video-result-item').length > 0) {
                clearInterval(videoResultsCheck);
                clearTimeout(timeout);
                add_year_separator(videoResultsContainer);
            }
        } catch {}
    }, 50);
    
    // Stop checking for video results
    const timeout = setTimeout(() => {
        clearInterval(videoResultsCheck);
    }, 2000);
}

if (urlParams.get('sort-by') && urlParams.get('sort-by').includes('title')) {
    console.log('Adding movie title separator');
    // check if video results loaded
    const videoResultsCheck = setInterval(() => {
        try {
            if (videoResultsContainer.querySelectorAll('.video-result-item').length > 0) {
                clearInterval(videoResultsCheck);
                clearTimeout(timeout);
                add_movie_separator(videoResultsContainer);
            }
        } catch {}
    }, 50);
    
    // Stop checking for video results
    const timeout = setTimeout(() => {
        clearInterval(videoResultsCheck);
    }, 2000);
}

if (urlParams.get('sort-by') && urlParams.get('sort-by').includes('studio')) {
    console.log('Adding studio separator');
    // check if video results loaded
    const videoResultsCheck = setInterval(() => {
        try {
            if (videoResultsContainer.querySelectorAll('.video-result-item').length > 0) {
                clearInterval(videoResultsCheck);
                clearTimeout(timeout);
                add_studio_separator(videoResultsContainer);
            }
        } catch {}
    }, 50);
    
    // Stop checking for video results
    const timeout = setTimeout(() => {
        clearInterval(videoResultsCheck);
    }, 2000);
}