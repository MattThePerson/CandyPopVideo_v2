
import { injectComponents } from '../../shared/util/component.js'
injectComponents();


const response = await fetch('/api/hello');
const json = await response.json();
console.log(json);


