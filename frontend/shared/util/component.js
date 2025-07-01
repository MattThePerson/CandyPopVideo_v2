
import { Header } from "../components/Header.js";
import { Footer } from "../components/Footer.js";

const components = [Header, Footer];


export function injectComponents() {

    const componentMethods = Object.fromEntries(
        components.map(fn => [fn.name, fn])
    );

    document.querySelectorAll('.MyComponent').forEach(el => {
        const componentName = el.getAttribute("component");
        // console.log('componentName:', componentName);
        try {
            const html = componentMethods[componentName]();
            el.insertAdjacentHTML("afterend", html);
            el.remove();
        } catch (e) {
            console.error("ERROR: Unable to get html for component:", componentName);
        }
    });
    
}


