
import { injectComponents } from '../../shared/util/component.js'
injectComponents();


const response = await fetch('/api/get/curated-collections');
const data = await response.json();

const ul = $('main ul').get(0);
for (let tuple of data.collections) {
    const folder = tuple[0];
    const creation_time = tuple[1];
    const date = new Date(creation_time * 1000)
    const date_fmt = date.toISOString().slice(0, 16).replace('T', ' ');
    const li = document.createElement('li');
    li.innerHTML = /* html */`
        <span>${date_fmt}</span>
        <a href="/curated/${folder}/index.html" target="_blank">${folder}</a>
    `
    ul.appendChild(li);
}

