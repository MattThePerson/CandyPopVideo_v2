
import { injectComponents } from '../../shared/util/component.js'
import '../../shared/web-components/search_result_card.js';

injectComponents(); /* inject my custom components */


/* INSERT A BUNCH OF UNIQUE WEB COMPONENTS */
const container = document.querySelector('#items');
let html = '';

for (let i = 0; i < 4; i++) {
    html += /* html */`
        <search-result-card
            title="scene number ${i+1}"
            performer="Amanda Foxy"
        ></search-result-card>
    `
}

container.innerHTML = html;
