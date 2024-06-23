# 23.06.24

import time
from collections import deque
from threading import Thread, Lock


# External library
import psutil
import tkinter as tk


class NetworkMonitor:
    def __init__(self, maxlen=10):
        self.speeds = deque(maxlen=maxlen)
        self.lock = Lock()

    def capture_speed(self, interval: float = 0.5):
        def get_network_io():
            io_counters = psutil.net_io_counters()
            return io_counters

        def format_bytes(bytes):
            if bytes < 1024:
                return f"{bytes:.2f} Bytes/s"
            elif bytes < 1024 * 1024:
                return f"{bytes / 1024:.2f} KB/s"
            else:
                return f"{bytes / (1024 * 1024):.2f} MB/s"

        old_value = get_network_io()
        while True:
            time.sleep(interval)
            new_value = get_network_io()

            with self.lock:
                upload_speed = (new_value.bytes_sent - old_value.bytes_sent) / interval
                download_speed = (new_value.bytes_recv - old_value.bytes_recv) / interval
                
                self.speeds.append({
                    "upload": format_bytes(upload_speed),
                    "download": format_bytes(download_speed)
                })

                old_value = new_value


class NetworkMonitorApp:
    def __init__(self, root):
        self.monitor = NetworkMonitor()
        self.root = root
        self.root.title("Network Bandwidth Monitor")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        self.label_upload_header = tk.Label(text="Upload Speed:", font="Quicksand 12 bold")
        self.label_upload_header.pack()

        self.label_upload = tk.Label(text="Calculating...", font="Quicksand 12")
        self.label_upload.pack()

        self.label_download_header = tk.Label(text="Download Speed:", font="Quicksand 12 bold")
        self.label_download_header.pack()

        self.label_download = tk.Label(text="Calculating...", font="Quicksand 12")
        self.label_download.pack()

        self.attribution = tk.Label(text="\n~ WaterrMalann ~", font="Quicksand 11 italic")
        self.attribution.pack()

        self.update_gui()
        self.start_monitoring()

    def update_gui(self):
        with self.monitor.lock:
            if self.monitor.speeds:
                latest_speeds = self.monitor.speeds[-1]
                self.label_upload.config(text=latest_speeds["upload"])
                self.label_download.config(text=latest_speeds["download"])

        self.root.after(250, self.update_gui)  # Update every 0.25 seconds

    def start_monitoring(self):
        self.monitor_thread = Thread(target=self.monitor.capture_speed, args=(0.5,), daemon=True)
        self.monitor_thread.start()



root = tk.Tk()
app = NetworkMonitorApp(root)
root.mainloop()
