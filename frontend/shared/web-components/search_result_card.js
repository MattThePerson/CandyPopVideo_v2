
/* SearchResultCard */
export class MyCard extends HTMLElement {

    constructor() {
        super();
    }

    connectedCallback() {
        console.log("Custom element added to page.");
        this.render();
    }

    disconnectedCallback() {
        console.log("Custom element removed from page.");
    }

    connectedMoveCallback() {
        console.log("Custom element moved with moveBefore()");
    }

    adoptedCallback() {
        console.log("Custom element moved to new page.");
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log(`Attribute ${name} has changed.`);
    }

    /* RENDER */

    render() {
        const shadow = this.attachShadow({ mode: "open" });

        /* html */
        const element = document.createElement('div');
        element.innerHTML = /* html */`
            <h2>${this.getAttribute("title")}</h2>
            <h3>${this.getAttribute("performer")}</h3>

        `;
        
        /* styles */
        const styles = document.createElement("style");
        styles.textContent = /* css */`
            div {
                padding: 10px;
                border: 1px solid #ccc;
                background: orange;
            }
        `;
        
        shadow.appendChild(styles);
        shadow.appendChild(element);
    }
    
}
customElements.define('search-result-card', MyCard);


