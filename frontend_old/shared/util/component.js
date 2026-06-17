
import { Header } from "../components/Header.js";
import { Footer } from "../components/Footer.js";

// function Twaddle() {
//     return /* html */`
//         <h2>here stupid</h2>
//         <script defer>
//             console.log('from the twaddle:',window.location.href);
//         </script>
//     `;
// }

const components = [
    // Twaddle,
    Header,
    Footer,
];


export function injectComponents() {

    const componentMethods = Object.fromEntries(
        components.map(func => [func.name.toLowerCase(), func])
    );
    
    let components_added = -1;
    while (components_added !== 0) {
        components_added = 0;

        for (let [name, func] of Object.entries(componentMethods)) {
            document.querySelectorAll(`custom-${name}:not(.loaded)`).forEach(el => {
                // console.log('adding: custom-'+name);
                try {
                    el.innerHTML = func();
                    el.querySelectorAll('script').forEach(script => {
                        const new_script = document.createElement('script');
                        new_script.defer = true;
                        if (script.src) {
                            new_script.src = script.src;
                        } else {
                            new_script.textContent = script.textContent;
                        }
                        document.head.appendChild(new_script);
                        script.remove();
                    })
                    el.classList.add('loaded');
                    components_added++;
                } catch (err) {
                    console.error(`ERROR: Unable to inject html for component 'component-${name}': ${err}`);
                }
            });
        }
        // console.log('components_added:', components_added);
    }

    
}


