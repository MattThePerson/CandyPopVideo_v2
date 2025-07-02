
import { Header } from "../components/Header.js";
import { Footer } from "../components/Footer.js";

const components = [
    Header,
    Footer,
];


export function injectComponents() {

    const componentMethods = Object.fromEntries(
        components.map(fn => [fn.name, fn])
    );

    document.querySelectorAll('.MyComponent').forEach(el => {
        const componentName = el.getAttribute("component");
        // console.log('componentName:', componentName);
        try {
            const html = componentMethods[componentName]();
            el.innerHTML = html;
            el.querySelectorAll('script').forEach(script => {
                const newScript = document.createElement('script');
                if (script.src) {
                    newScript.src = script.src;
                } else {
                    newScript.textContent = script.textContent;
                }
                document.head.appendChild(newScript);
            });
        } catch (err) {
            console.error(`ERROR: Unable to inject html for component '${componentName}': ${err}`);
        }
    });
    
}


