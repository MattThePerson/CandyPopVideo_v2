from pystray import Icon, Menu, MenuItem
from PIL import Image
import webbrowser
import threading
from ProcessManager import ProcessManager
import time
import signal
import yaml
import subprocess
import os
import sys
import platform
import pyperclip

# Add python venv binaries to PATH (if ever switching to go)
# base_dir = os.path.dirname(os.path.abspath(sys.executable))
# print('base_dir:', base_dir)
# venv_path = os.path.join(base_dir, ".venv")
# if os.name == "nt": # Windows
#     os.environ["PATH"] = os.path.join(venv_path, "Scripts") + os.pathsep + os.environ["PATH"]
# else:
#     os.environ["PATH"] = os.path.join(venv_path, "bin") + os.pathsep + os.environ["PATH"]



#region - GLOBALS ------------------------------------------------------------------------------------------------------

# load config
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

os.environ["DEV_MODE"] = "1"

# PROCESSES

PORT = 8011
APP_URL = f'http://localhost:{PORT}'
SERVER_PROC = ProcessManager(
    [sys.executable, '-m', 'uvicorn', 'src.main:app', '--host', '0.0.0.0', '--port', str(PORT)],
    '.logs/tray_app/server.log',
)


#region - METHODS ------------------------------------------------------------------------------------------------------

def start_backend():
    icon.title = 'Starting backend ...'
    print('Starting backend ...')
    SERVER_PROC.start()
    icon.title = 'Backend running!'
    print('Backend running!')
    update_tray_icon_menu(icon)

def restart_backend():
    print('Stopping')
    SERVER_PROC.stop()
    print('Starting')
    SERVER_PROC.start()
    print('Done')

def stop_backend():
    icon.title = 'Stopping backend ...'
    print('Stopping backend ...')
    SERVER_PROC.stop()
    icon.title = 'Backend stopped'
    print('Backend stopped')
    update_tray_icon_menu(icon)

SERVER_PROC_is_running = False
def backend_is_running():
    return SERVER_PROC.is_running() or False


def quit_app():
    SERVER_PROC.stop()
    icon.stop()


#region - OPEN RESOURCES -----------------------------------------------------------------------------------------------

def open_url(url):
    webbrowser.open(APP_URL)

def open_url_in_browser(url, browser):
    browser_paths = {
        'Brave': {
            'win32': [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
            ],
            'darwin': ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"],
            'linux': ["brave-browser", "brave"],
        },
        'Firefox': {
            'win32': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            'darwin': ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            'linux': ["firefox"],
        },
        'Chrome': {
            'win32': [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ],
            'darwin': ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            'linux': ["google-chrome", "chrome", "chromium-browser", "chromium"],
        }
    }
    for path in browser_paths[browser].get(sys.platform, []):
        try:
            if sys.platform == 'win32':
                subprocess.Popen([path, APP_URL])
            elif sys.platform == 'darwin':
                subprocess.Popen([path, APP_URL])
            else: # Linux or others
                subprocess.Popen([path, APP_URL])
            return True
        except FileNotFoundError:
            continue


def copy_app_url():
    ...

def scan_libraries():
    icon.title = 'Scanning ...'




def open_file(path: str):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else: # Linux
        subprocess.run(["xdg-open", path])

def open_folder(path: str):
    if platform.system() == "Windows":
        os.startfile(os.path.abspath(path))
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else: # Linux
        subprocess.run(["xdg-open", path])

start_on_login = True
def toggle_start_on_login():
    global start_on_login
    start_on_login = not start_on_login


#region - TRAY ICON MENU -----------------------------------------------------------------------------------------------

def update_tray_icon_menu(icon):
    icon.menu = Menu(
        MenuItem("Open App",                    lambda icon, item: open_url(APP_URL)),
        MenuItem("Open App in ...", Menu(
            MenuItem('Brave',                   lambda: open_url_in_browser(APP_URL, 'Brave')),
            MenuItem('Firefox',                 lambda: open_url_in_browser(APP_URL, 'Firefox')),
            MenuItem('Chrome',                  lambda: open_url_in_browser(APP_URL, 'Chrome')),
        )),
        MenuItem("Copy App URL",                lambda: pyperclip.copy(APP_URL)),
        Menu.SEPARATOR,
        MenuItem("Start App",                   lambda icon, item: start_backend(),             enabled=not backend_is_running()),
        MenuItem("Restart App",                 lambda icon, item: restart_backend(),           enabled=backend_is_running()),
        MenuItem("Stop App",                    lambda icon, item: stop_backend(),              enabled=backend_is_running()),
        MenuItem("Restart on Crash",            lambda icon, item: toggle_start_on_login(),         checked=lambda item: start_on_login),
        Menu.SEPARATOR,
        MenuItem("Scan Libraries", Menu(
            MenuItem('Quick Scan',              lambda: ...),
            MenuItem('Redo Parsing',            lambda: ...),
            MenuItem('Redo Hashing',            lambda: ...),
        ), enabled=True),
        MenuItem("Generate Media", Menu(
            MenuItem('For 10 videos',           lambda: ...),
            MenuItem('For 50 videos',           lambda: ...),
            MenuItem('For 150 videos',          lambda: ...),
            MenuItem('Added in last 24 hours',  lambda: ...),
            MenuItem('Added in last 48 hours',  lambda: ...),
            MenuItem('All',                     lambda: ...),
        ), enabled=True),
        MenuItem("Interrupt worker",            lambda icon, item: ...,                             enabled=False),
        Menu.SEPARATOR,
        MenuItem("Open config.yaml",            lambda: open_file('config.yaml')),
        MenuItem("Open Folder", Menu(
            MenuItem('App Data folder',         lambda: open_folder( CONFIG.get('app_data_dir') )),
            MenuItem('Project folder',          lambda: open_folder( get_root_path() )), 
            MenuItem('Logs folder',             lambda: open_folder( get_logsdir_path() )), 
        )),
        MenuItem("Open Logs", Menu(
            MenuItem('Server Logs',             lambda: open_file( get_latest_logfile('server') )),
            MenuItem('Worker Logs',             lambda: ...),
        )),
        Menu.SEPARATOR,
        MenuItem("Quit",                        lambda icon, item: quit_app()),
    )


#region - HELPERS ------------------------------------------------------------------------------------------------------

def get_root_path():
    if getattr(sys, 'frozen', False):
        file = sys.executable
    else:
        file = os.path.dirname(__file__)
    return os.path.dirname(os.path.abspath(file))

def get_logsdir_path():
    return os.path.join( get_root_path(), '.logs', 'tray_app' )

def get_latest_logfile(root):
    logsdir = get_logsdir_path()
    return [ os.path.join(logsdir, f) for f in os.listdir(logsdir) if f.startswith(root) ][0]


#region - START --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    icon = Icon(
        "CandyPop Video",
        Image.open("assets/icon.png"),
    )
    icon.title = 'CandyPop Video Launcher'
    update_tray_icon_menu(icon)

    icon_thread = threading.Thread(target=icon.run)

    print('Starting tray icon thread')
    icon_thread.start()

    # INTERRUPT STUFF
    signal.signal(signal.SIGINT, lambda sig, frm: icon.stop())
    try:
        while icon_thread.is_alive():
            icon_thread.join(timeout=0.5)
    except KeyboardInterrupt:
        print("Keyboard interrupt caught in main thread")
        icon.stop()
        icon_thread.join()

    print('Done.')
    