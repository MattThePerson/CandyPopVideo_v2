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

# Add python venv binaries to PATH (if ever switching to go)
# base_dir = os.path.dirname(os.path.abspath(sys.executable))
# print('base_dir:', base_dir)
# venv_path = os.path.join(base_dir, ".venv")
# if os.name == "nt": # Windows
#     os.environ["PATH"] = os.path.join(venv_path, "Scripts") + os.pathsep + os.environ["PATH"]
# else:
#     os.environ["PATH"] = os.path.join(venv_path, "bin") + os.pathsep + os.environ["PATH"]


# ...

PORT = 8010
APP_URL = f'http://localhost:{PORT}'

# load config
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)


# PROCESSES

backend_proc = ProcessManager([sys.executable, '-m', 'uvicorn', 'src.main:app', '--host', '0.0.0.0', '--port', str(PORT)])

def start_backend(icon):
    icon.title = 'Starting backend ...'
    print('Starting backend ...')
    backend_proc.start()
    icon.title = 'Backend running!'
    print('Backend running!')
    update_tray_icon_menu(icon)

def restart_backend():
    subprocess.run(['where.exe', 'python'])

def stop_backend():
    icon.title = 'Stopping backend ...'
    print('Stopping backend ...')
    backend_proc.stop()
    icon.title = 'Backend stopped'
    print('Backend stopped')
    update_tray_icon_menu(icon)

backend_proc_is_running = False
def backend_is_running():
    return backend_proc.is_running() or False


#region - OPEN RESOURCES -----------------------------------------------------------------------------------------------

def open_app():
    webbrowser.open(APP_URL)

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


#region - HELPERS ------------------------------------------------------------------------------------------------------

def get_self_path():
    return os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))


#region - TRAY ICON MENU -----------------------------------------------------------------------------------------------

def update_tray_icon_menu(icon):
    icon.menu = Menu(
        MenuItem("Open App", open_app),
        MenuItem("Open App in ...", Menu(
            MenuItem('Brave',                   lambda: ...),
            MenuItem('Firefox',                 lambda: ...),
            MenuItem('Chrome',                  lambda: ...),
        )),
        MenuItem("Copy App URL",                lambda: ...),
        Menu.SEPARATOR,
        MenuItem("Start App",                   lambda icon, item: start_backend(icon),             enabled=not backend_is_running()),
        MenuItem("Restart App",                 restart_backend,                                    enabled=backend_is_running()),
        MenuItem("Stop App",                    stop_backend,                                       enabled=backend_is_running()),
        MenuItem("Restart on Crash",            toggle_start_on_login,                              checked=lambda item: start_on_login),
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
        MenuItem("Open config.yaml",            lambda icon, item: open_file('config.yaml')),
        MenuItem("Open folder", Menu(
            MenuItem('App Data folder',         lambda: open_folder( CONFIG.get('app_data_dir') )),
            MenuItem('Project folder',          lambda: open_folder( get_self_path() )), 
            MenuItem('Logs folder',             lambda: ...), 
        )),
        # MenuItem("Open Logs", Menu(
        #     MenuItem('Server Logs',             lambda: ...),
        #     MenuItem('Manager LOgs',            lambda: ...),
        # )),
        Menu.SEPARATOR,
        MenuItem("Quit",                        lambda icon, item: icon.stop()),
    )


#region - START --------------------------------------------------------------------------------------------------------

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
