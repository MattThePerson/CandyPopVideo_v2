import subprocess
import threading

class ProcessManager:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process: None|subprocess.Popen = None
        self.status = "stopped"
        self._stdout_thread = None
        self._stop_reading = threading.Event()

    def start(self):
        if self.process and self.process.poll() is None:
            print("Process already running")
            return
        self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.status = "running"
        self._stop_reading.clear()
        self._stdout_thread = threading.Thread(target=self._read_stdout)
        self._stdout_thread.start()

    def _read_stdout(self):
        for line in self.process.stdout:
            if self._stop_reading.is_set():
                break
            print(f"[{self.cmd[0]}] {line.strip()}")
            # Optionally parse lines to update status here

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.status = "stopped"
        self._stop_reading.set()
        if self._stdout_thread:
            self._stdout_thread.join()

    def restart(self):
        self.stop()
        self.start()

    def is_running(self):
        return self.process and self.process.poll() is None

    def get_status(self):
        return self.status
