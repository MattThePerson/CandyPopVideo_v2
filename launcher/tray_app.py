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

while not os.path.exists("LICENSE"):
    os.chdir("..")


# load config
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

os.environ["DEV_MODE"] = "1"

GO_EXE_STEM = "bin/CandyPopVideo"
if platform.system() == "Windows":
    GO_SERVER_EXE = GO_EXE_STEM + ".exe"
else:
    GO_SERVER_EXE = GO_EXE_STEM

# PROCESSES

PORT = 8010
APP_URL = f'http://localhost:{PORT}'
# SERVER_PROC_PYTHON = ProcessManager(
#     [sys.executable, '-m', 'uvicorn', 'python_src.main:app', '--host', '0.0.0.0', '--port', str(PORT)],
#     '.logs/tray_app/server.log',
# )

WORKER_PROC = ProcessManager(None, ".logs/tray_app/worker.log")

SERVER_PROC = ProcessManager(
    [GO_SERVER_EXE, "--port", str(PORT)] + sys.argv[1:],
    ".logs/tray_app/server.log",
)

def build_backend():
    result = subprocess.run(
        [
            "go", "build",
            "-C", "go_backend",
            "-ldflags=-s -w",
            "-o", f"../{GO_SERVER_EXE}"
        ],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    if result.returncode != 0:
        raise Exception(f"Failed with code {result.returncode}\nSTDERR: {result.stderr}")

#region - SERVER ------------------------------------------------------------------------------------------------------


# launch_backend
def launch_backend():
    rebuild_backend()
    start_backend()


# relaunch_backend
def relaunch_backend():
    stop_backend()
    rebuild_backend()
    start_backend()


# 
def rebuild_backend():
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/gear_yellow.png", wid=0.45)
    update_title("go build... ")
    s = time.time()
    build_backend()
    update_title("took {:.2f}s\n".format(time.time()-s))
    update_tray_icon_menu(icon)

# 
def start_backend():
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/good.png")
    update_title("running server\n")
    SERVER_PROC.start(onfail=lambda err: show_process_fail(err))
    update_tray_icon_menu(icon)

# 
def stop_backend():
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/down.png")
    update_title("stopping server\n")
    SERVER_PROC.stop()
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/idle_grey.png")
    update_tray_icon_menu(icon)


def show_process_fail(err):
    update_title("subprocess failed\n")
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/error.png")
    print("SUBPROCESS FAILED:", err)

SERVER_PROC_is_running = False
def backend_is_running():
    return SERVER_PROC.is_running() or False


def quit_app():
    SERVER_PROC.stop()
    icon.stop()



#region - WORKER -------------------------------------------------------------------------------------------------------

def do_quick_scan(item):
    print("ITEM:", item)
    
    WORKER_PROC.init([
        sys.executable, "-m", "python_src.worker",
        # "--scan-libraries"
        "-ms", "all", "-f", "Aidra Fox",
    ])
    
    s = time.time()
    update_title("worker: quick scan\n")
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/gear_yellow.png", wid=0.45)
    WORKER_PROC.start()
    WORKER_PROC.join()
    time.sleep(1)
    update_title("quick_scan took {:.0f}s\n".format(time.time()-s))
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/good.png")
    


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
        MenuItem("Scan Libraries", Menu(
            MenuItem('Quick Scan',              lambda icon, item: do_quick_scan(item)),
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
        MenuItem("Start App",                   lambda icon, item: launch_backend(),             enabled=not backend_is_running()),
        MenuItem("Restart App",                 lambda icon, item: relaunch_backend(),           enabled=backend_is_running()),
        MenuItem("Stop App",                    lambda icon, item: stop_backend(),              enabled=backend_is_running()),
        # MenuItem("Restart on Crash",            lambda icon, item: toggle_start_on_login(),         checked=lambda item: start_on_login),
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


def combine_icons(base_path, overlay_path, wid=0.4):
    base = Image.open(base_path).convert("RGBA")
    overlay = Image.open(overlay_path).convert("RGBA")

    # Resize overlay to 40% of base width, maintain aspect ratio
    new_width = int(base.width * wid)
    aspect_ratio = overlay.height / overlay.width
    overlay_resized = overlay.resize((new_width, int(new_width * aspect_ratio)))

    # Position at bottom-right
    x = base.width - overlay_resized.width
    y = base.height - overlay_resized.height

    # Composite
    base.paste(overlay_resized, (x, y), overlay_resized)
    return base



def update_tray_app(prnt: str|None=None, subicon: str|None=None, subicon_wid=0.4):
    if prnt:    print(prnt)
    # if title:   icon.title = title
    if subicon: icon.icon = combine_icons("assets/icon.png", "assets/"+subicon, subicon_wid)
    update_tray_icon_menu(icon)


TITLE = ""
def update_title(txt, noprint=False):
    global TITLE
    TITLE = (TITLE + txt)[128:]
    icon.title = TITLE
    if not noprint:
        print(f"[LAUNCHER] {txt}", end="")


#region - START --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    icon = Icon(
        "CandyPop Video",
        Image.open("assets/icon.png"),
    )
    icon.title = 'CandyPop Video Launcher'
    icon.icon = combine_icons("assets/icon.png", "assets/subicons/idle_grey.png")
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
    