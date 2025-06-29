
let item_amounts;
let listedItems = [];


/* FUNCTIONS */

function addLetterNav() {
    const letterNav = document.querySelector(".letter-nav");
    for (let letter of "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('')) {
        let letterButton = document.createElement("button");
        letterButton.classList.add("letter-nav-btn");
        letterButton.textContent = letter;
        letterButton.addEventListener('click', e => {
            let letterSection = document.getElementById("letter-section-"+letter);
            letterSection.scrollIntoView({ behavior: "smooth"});
            letterSection.classList.add('highlighted-section');
            setTimeout(() => {
                letterSection.classList.remove('highlighted-section');
            }, 0);
        });
        letterNav.appendChild(letterButton);
    }
}

function populateCatalogue(listedItems) {
    const content = document.getElementById("content");
    const letterTemplate = document.getElementById("item-starting-letter-template");
    const rowTemplate = document.getElementById("item-row-template");
    for (let letter of "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('')) {
        let letterClone = letterTemplate.content.cloneNode(true);
        let listItem = letterClone.querySelector("li");
        listItem.id = `letter-section-${letter}`;
        letterClone.querySelector(".letter").textContent = letter;
        listItem.querySelector(".letter").addEventListener('click', e => {
            document.querySelector("header").scrollIntoView({behavior: "smooth"})
        });
        let startingLetterItems = [];
        listedItems.forEach(item => {
            if (item[0].toLowerCase() === letter.toLowerCase()) {
                startingLetterItems.push(item);
            }
        })
        /* console.log(startingLetterItems); */
        for (let item of startingLetterItems) {
            let rowClone = rowTemplate.content.cloneNode(true);
            let type = urlParams.get('type');
            let qparams = new URLSearchParams();
            qparams.set(urlParams.get('type'), item)
            rowClone.querySelector(".row").href = 'searchPage.html?' + String(qparams);
            //`index.html?${urlParams.get('type')}=${nameFmt}`;
            rowClone.querySelector(".item-name").textContent = item;
            rowClone.querySelector(".gallery-amount").textContent = item_amounts[item];
            listItem.appendChild(rowClone);
        }
        if (startingLetterItems.length == 0) {
            let emptyRow = document.createElement("span");
            emptyRow.classList.add("empty-row");
            emptyRow.textContent = "...";
            listItem.appendChild(emptyRow);
        }
        if (startingLetterItems.length > 0) {
            content.appendChild(letterClone);
        }
    }
    updateContentSectionHeight();
}

function updateContentSectionHeight() {
    const content = document.getElementById("content");
    let viewWidth = window.innerWidth;
    let columns = Math.floor(viewWidth/300);
    let heightRem = listedItems.length*2.7/columns;
    content.style.height = `${heightRem}rem`;
    console.log("updated content height");
}

function clearCatalogue() {
    const content = document.getElementById("content");
    content.innerHTML = "";
}

function filterItems(dict, thresh) {
    let items = [];
    Object.keys(dict).forEach(item => {
        if (dict[item] >= thresh) {
            items.push(item);
        }
    })
    return items;
}

/* EVENT LISTENERS */

const threshSlider = document.getElementById("thresh-slider");
const threshShow = document.querySelector(".slider-container .value");
threshSlider.value = 10;
threshShow.textContent = threshSlider.value;
threshSlider.oninput = function() {
    galleryAmountThresh = this.value;
    threshShow.textContent = this.value;
    clearCatalogue();
    listedItems = filterItems(item_amounts, galleryAmountThresh);
    populateCatalogue(listedItems);
}

window.onresize = updateContentSectionHeight;


/* API CALL */

const catalogue_type = urlParams.get('type');
document.querySelector('.page-title').innerText = catalogue_type + ' Catalogue';
document.title = catalogue_type + ' Catalogue Page';
let api_call = 'api/get/all-' + catalogue_type + 's';

makeApiRequestGET(api_call, [], results => {
    console.log('Got ' + results.length + ' catalogue results for type: ' + catalogue_type);
    console.log(results);
    item_amounts = results;
    addLetterNav();
    clearCatalogue();
    listedItems = filterItems(item_amounts, threshSlider.value);
    populateCatalogue(listedItems);
});

