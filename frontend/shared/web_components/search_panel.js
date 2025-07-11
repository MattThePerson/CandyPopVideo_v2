
/* SearchResultCard */
class MyCard extends HTMLElement {

    constructor() {
        super();
    }

    async connectedCallback() {
        this.attachShadow({ mode: 'open' });
        
        /* fetch get styles */
        const response = await fetch('/shared/web_components/search_panel.css');
        const css = await response.text()
        this.render(css);

        this.addEventListeners();
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

    /* EVENT LISTENERS */

    addEventListeners() {
        const $shadow = $(this.shadowRoot);

        /* focus search input with tab if not already in search panel */
        $(document).on('keydown', e => {
            if (e.key === 'Tab') {
                if (document.activeElement.localName !== 'search-panel') {
                    e.preventDefault();
                    $shadow.find('input.search').focus();
                }

            }
        });
    }
    
    /* RENDER */

    render(css) {
        
        this.shadowRoot.innerHTML = /* html */`
        
            <!-- html ----------------------------------------------------------------------------->

            <div class="container">
                
                <!-- PANEL -->
                <section class="panel">
                    
                    <!-- top bar -->
                    <div class="top-bar">
                        <div class="left-side">
                            <button class="apply">apply</button>
                            <button class="search">
                                <svg fill="#fff" width="1.2rem" height="1.2rem" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12.027 9.92L16 13.95 14 16l-4.075-3.976A6.465 6.465 0 0 1 6.5 13C2.91 13 0 10.083 0 6.5 0 2.91 2.917 0 6.5 0 10.09 0 13 2.917 13 6.5a6.463 6.463 0 0 1-.973 3.42zM1.997 6.452c0 2.48 2.014 4.5 4.5 4.5 2.48 0 4.5-2.015 4.5-4.5 0-2.48-2.015-4.5-4.5-4.5-2.48 0-4.5 2.014-4.5 4.5z" fill-rule="evenodd"/>
                                </svg>
                            </button>
                            <input type="text" class="search" placeholder="search query ...">
                        </div>
                        <div class="right-side">
                            <div>sort by</div>
                            <div class="sortby-selector">date added asc</div>
                        </div>
                        
                    </div>

                    <!-- body -->
                    <div class="panel-body">
                        
                        <div class="tag-filters-section">
                            <h3>tag filters</h3>
                            <div class="tag-filters-container">
                                <div class="column">
                                    <div class="holder">
                                        <h4>actors</h4>
                                        <input type="text">
                                    </div>
                                    <div class="holder">
                                        <h4>studio</h4>
                                        <input type="text">
                                    </div>
                                    <div class="holder">
                                        <h4>collection</h4>
                                        <input type="text">
                                    </div>
                                </div>
                                <div class="column">
                                    <div class="holder">
                                        <h4>include</h4>
                                        <input type="text">
                                    </div>
                                    <div class="holder">
                                        <h4>exclude</h4>
                                        <input type="text">
                                    </div>
                                    <div class="holder">
                                        <h4>tags</h4>
                                        <input type="text">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="attribute-filters-section">
                            <h3>video filters</h3>
                            <div class="attribute-filters-container">
                                <div class="wrapper">
                                    <button class="remove-filter">
                                        -
                                    </button>
                                    <div class="holder">
                                        <h5>resolution</h5>
                                        <input type="text">
                                    </div>
                                </div>
                                <div class="wrapper">
                                    <button class="remove-filter">
                                        -
                                    </button>
                                    <div class="holder">
                                        <h5>fps</h5>
                                        <input type="text">
                                    </div>
                                </div>
                                <div class="wrapper">
                                    <button class="add-filter">
                                        +
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                    </div>
                    
                    <!-- bottom bar -->
                    <div class="bottom-bar">
                        <div class="left-side">
                            <!-- <button class="hide-extension">hide</button> -->
                            <button class="date-added-dist">date added dist</button>
                            <button class="date-released-dist">date released dist</button>
                            <button class="word-cloud">word cloud</button>
                            <button class="disabled similar-performers">similar performers</button>
                            <button class="disabled similar-studios">similar studios</button>
                        </div>
                        <div class="right-side">
                            <button class="random-video">random video</button>
                        </div>
                    </div>
                    
                </section>

                <!-- EXTENSIONS -->
                <section class="extensions">
                    
                </section>
            </div>

            <style>
                ${css}
            </style>
            
            
        `;
    }
    
}
customElements.define('search-panel', MyCard);


