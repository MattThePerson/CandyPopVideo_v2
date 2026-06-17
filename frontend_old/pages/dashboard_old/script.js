
import { injectComponents } from '../../shared/util/component.js'
import { makeApiRequestGET } from '../../shared/util/request.js'

injectComponents();


//region - GLOBAL VARIABLES --------------------------------------------------------------------------------------------

const terminal = document.querySelector('#terminal');
const textBox =  terminal.querySelector('.text-box');
const input =    terminal.querySelector('input');

const statusButton =    document.querySelector('#websocket-status-button');
const clearButton =   document.querySelector('#clear-button');
const interruptButton = document.querySelector('#interrupt-button');
const helpButton = document.querySelector('#help-button');


/* terminal history */

let cache;
cache = localStorage.getItem('terminal_command_history');
let command_history = cache ? JSON.parse(cache) : [];
let command_idx = 0;

cache = localStorage.getItem('terminal_msg_history');
let msg_history = cache ? JSON.parse(cache) : [];

msg_history.forEach(html => addLineRaw(html, textBox));


/* init web socket */
let socket;


//region - FUNCTIONS ---------------------------------------------------------------------------------------------------

function connectWebsocket() {

    setStatusButtonClass(statusButton, 'connecting');
    
    makeApiRequestGET('/api/get-port', [], res => {
        console.log('port number:', res.port);

        socket = new WebSocket(`ws://localhost:${res.port}/terminal`);
    
        socket.onopen = () => {
            addLine('websocket connected', textBox);
            setStatusButtonClass(statusButton, 'connected');
        };
        
        socket.onclose = (event) => {
            addLine('websocket disconnected', textBox);
            setStatusButtonClass(statusButton, 'disconnected');
        };
        
        socket.onmessage = (event) => {
            // console.log(event.data);
            addLines(event.data, textBox);
        };
    });

}



function terminalEnter(msg, textBox, socket=null) {
    addCommandLine(msg, textBox);
    if (socket) {
        socket.send(msg);
    }
    input.value = '';
    const idx = command_history.indexOf(msg);
    if (idx > -1) command_history.splice(idx, 1);
    command_history.unshift(msg);
    command_idx = -1;
}

function clearTerminal(textBox, hist=false) {
    textBox.innerHTML = '';
    if (hist) {
        msg_history = [];
        command_history = [];
    }
}

function addLineRaw(html, textBox) {
    // console.log('adding raw html:', html);
    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = html;
    textBox.appendChild(line);
    textBox.scrollTop = textBox.scrollHeight;
}

function addCommandLine(text, textBox) {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = `
        <div class="line-start-arrow">></div>
        <div>${text}</div>
    `;
    textBox.appendChild(line);
    textBox.scrollTop = textBox.scrollHeight;
    msg_history.push(line.innerHTML);
    terminal.scrollTop = terminal.scrollHeight
}

function addLine(text, textBox) {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = `<div>${text}</div>`;
    textBox.appendChild(line);
    textBox.scrollTop = textBox.scrollHeight;
    msg_history.push(line.innerHTML);
    terminal.scrollTop = terminal.scrollHeight
}

function addLines(text, textBox) {
    text.split('\n').forEach(txt => addLine(txt, textBox))
}

function printHelp(textBox) {
    const help_text = `Welcome to CandyPop Videos backend manager! (using WebSockets!)

Interact as you would with a CLI tool, except you only need the arguments.

eg. --help
`;
    addLines(help_text, textBox);
}


function setStatusButtonClass(btn, cls) {
    for (let class_ of ['connecting', 'connected', 'disconnected']) {
        btn.classList.remove(class_);
    }
    btn.classList.add(cls);
    btn.textContent = cls;
}



//region - EVENT LISTENERS ---------------------------------------------------------------------------------------------

statusButton.addEventListener('mouseenter', () => {
    if (statusButton.classList.contains('disconnected')) statusButton.textContent = 'reconnect';
});
statusButton.addEventListener('mouseleave', () => {
    if (statusButton.classList.contains('disconnected')) statusButton.textContent = 'disconnected';
});

helpButton.onclick = () => {
    addLineRaw(`
        <div class="line-start-arrow">></div>
        <div>help</div>
    `, textBox);
    printHelp(textBox);
}

interruptButton.onclick = () => {
    addLine('sending interrupt to backend', textBox)
    socket.send('__INTERRUPT__');
}

/* save terminal history */
window.addEventListener('beforeunload', () => {
    localStorage.setItem("terminal_command_history", JSON.stringify(command_history));
    localStorage.setItem("terminal_msg_history", JSON.stringify(msg_history));
});

document.addEventListener('keydown', e => {
    if (!e.ctrlKey) {
        input.focus();
    }
});

input.addEventListener('keydown', (e) => {
    if (document.activeElement !== document.querySelector('#nav-bar-search-input')) {
        switch (e.key) {
            
            case 'Enter':
                if (input.value === 'clear' || input.value === 'cls') {
                    terminalEnter(input.value, textBox)
                    clearTerminal(textBox);
                } else if (input.value === 'clear-history') {
                    terminalEnter(input.value, textBox);
                    clearTerminal(textBox, true);
                } else if (input.value === 'help') {
                    terminalEnter(input.value, textBox);
                    printHelp(textBox);
                } else if (input.value === 'connect') {
                    terminalEnter(input.value, textBox);
                    connectWebsocket();
                } else {
                    terminalEnter(input.value, textBox, socket);
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                command_idx = Math.min(command_idx+1, command_history.length-1);
                input.value = (command_idx > -1) ? command_history[command_idx] : '';
                break;
                
            case 'ArrowDown':
                command_idx = Math.max(command_idx-1, -1);
                input.value = (command_idx > -1) ? command_history[command_idx] : '';
                break;
                
            default:
                command_idx = -1;
        }
    }
});


//region - MAIN ---------------------------------------------------------------------------------------------

connectWebsocket();

statusButton.onclick = () => {
    if (socket.readyState === WebSocket.CLOSED) {
        connectWebsocket();
    }
}

clearButton.onclick = () => { clearTerminal(textBox, true) }

document.querySelectorAll('button.common-option-button').forEach(button => {
    button.onclick = () => {
        const command = button.textContent
        terminalEnter(command, textBox, socket);
    };
});

const addedWithinButton = document.querySelector('.added-within-option');
const now = new Date(); // Current datetime
const twentyFourHoursAgo = new Date(now.getTime() - (2 * 24 * 60 * 60 * 1000));
const dateAddedFrom = twentyFourHoursAgo.toISOString().slice(0, 10);
// console.log(dateAddedFrom);
addedWithinButton.textContent += ' --date-added-from ' + dateAddedFrom;

