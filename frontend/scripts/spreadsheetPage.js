

/* FUNCTIONS */

function clearTable(spreadsheetContainer) {
    const headerEls = spreadsheetContainer.querySelectorAll('.header span');
    spreadsheetContainer.querySelector('.body-wrapper .body').innerHTML = '';
}

function addDataToTable(spreadsheetContainer, videos) {
    const headerEls = spreadsheetContainer.querySelectorAll('.header span');
    const tableBody = spreadsheetContainer.querySelector('.body');
    const headers = [];
    headerEls.forEach(el => headers.push(el.className));
    
    videos.forEach((video, index) => {
        const row = document.createElement('div');
        row.className = 'table-row';

        headers.forEach(header => {
            const cell = document.createElement('span');
            cell.classList.add(header);
            if (header == 'index') {
                cell.innerText = index+1;
            } else if (header == 'link') {
                let link = document.createElement('a');
                link.innerText = 'open';
                link.href = 'videoPage.html?hash=' + video.hash;
                link.target = '_blank';
                cell.appendChild(link);
            } else {
                cell.innerText = video[header];
            }
            if (!isNaN(cell.innerText))
                cell.classList.add('numeric');
            row.appendChild(cell);
        });
        
        tableBody.appendChild(row);
    })
}


function initializeTable(spreadsheetContainer) {
    const body = spreadsheetContainer.querySelector('.body')
    const headerEls = spreadsheetContainer.querySelectorAll('.header span');

    // construct columns
    headerEls.forEach(headerEl => {
        const header = headerEl.className;
        headerEl.parentElement.classList.add(header);
        console.log("Constructing header: " + header);

        // construct header cell
        const cell = document.createElement('div');
        cell.innerText = headerEl.className;
        if (['title', 'actor', 'studio', 'collection'].includes(header)) {
            const input = document.createElement('input');
            input.classList.add(header);
            headerEl.appendChild(input);
        }
        headerEl.appendChild(cell);
        
        // construct column
        // const column = document.createElement('div');
        // column.classList.add('column');
        // column.classList.add(header);
        // body.appendChild(column);
    });
}


function sortVideos(videos, header, ascending) {
    console.log("Sorting videos by " + header);
    videos.sort((a,b) => {
        const aa = a[header];
        const bb = b[header];
        if (!aa && !bb) {
            return 0;
        } else if (!aa) {
            return -1;
        } else if (!bb) {
            return 1;
        } else if (typeof aa === 'number') {
            return bb - aa;
        } else {
            return aa.localeCompare(bb, undefined, { sensitivity: 'accent' });
        }
    });
    if (!ascending)
        videos.reverse();
    videos.sort((a,b) => {
        if (!a[header]) {
            return 1;
        } else if (!b[header]) {
            return -1;
        } else {
            return 0;
        }
    });
}

/* SETUP & EVENT LISTENERS */

const videos = [];
let filtered = [];
const tableContainer = document.getElementById('spreadsheet-container');
let sortHeader = 'title';
let sortAscending = true;

initializeTable(tableContainer);

// add event listeners for sorting and filtering
document.querySelectorAll('#spreadsheet-container .header span').forEach(headerCell => {
    if (headerCell.className != 'index') {
        headerCell.querySelector('div').addEventListener('click', e => {
            clearTable(tableContainer);
            setTimeout(() => {
                let h = headerCell.className;
                if (h != sortHeader)
                    sortAscending = true;
                else
                    sortAscending = !sortAscending;
                sortHeader = h;
                sortVideos(filtered, sortHeader, sortAscending);
                addDataToTable(tableContainer, filtered);
            }, 1);
        });
    
        const input = headerCell.querySelector('input');
        if (input) {
            input.addEventListener('keydown', e => {
                if (e.key == 'Enter') {
                    clearTable(tableContainer);
                    setTimeout(() => {
                        const filterTerms = {};
                        document.querySelectorAll('#spreadsheet-container .header input').forEach(inp => {
                            const term = inp.value.toLowerCase();
                            if (term) {
                                const header = inp.parentElement.className;
                                filterTerms[header] = term;
                            }
                        });
                        filtered = videos.filter(vid => {
                            for (let [header, term] of Object.entries(filterTerms)) {
                                if (!(vid[header] && vid[header].toLowerCase().includes(term)))
                                    return false;
                            }
                            return true;
                        });
                        addDataToTable(tableContainer, filtered);
                    }, 1);
                }
            });
        }
    }
});


/* API CALLS */

let query = { limit: -1, startfrom: 0, search_query: '' };
makeApiRequestGET_JSON('search-videos', query, (search_results) => {
    console.log(search_results);
    for (let vid of search_results.videos)
        videos.push(vid);
    sortVideos(videos, sortHeader, true);
    filtered = videos;
    addDataToTable(tableContainer, filtered);
});





