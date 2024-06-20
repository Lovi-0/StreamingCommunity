# 20.02.24

import os
import time
import logging
import threading
from collections import deque


# External libraries
import psutil
from tqdm import tqdm


# Internal utilities
from Src.Util.color import Colors
from Src.Util.os import format_size
from Src.Util._jsonConfig import config_manager


# Variable
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')


class M3U8_Ts_Estimator:
    def __init__(self, total_segments: int):
        """
        Initialize the TSFileSizeCalculator object.

        Args:
            - total_segments (int): Len of total segments to download
        """
        self.ts_file_sizes = []
        self.now_downloaded_size = 0
        self.total_segments = total_segments
        self.lock = threading.Lock()
        self.speeds = deque(maxlen=3)
        self.speed_thread = threading.Thread(target=self.capture_speed)
        self.speed_thread.daemon = True
        self.speed_thread.start()

    def add_ts_file(self, size: int, size_download: int, duration: float):
        """
        Add a file size to the list of file sizes.

        Args:
            - size (int): The size of the ts file to be added.
            - size_download (int): Single size of the ts file.
            - duration (float): Time to download segment file.
        """
        if size <= 0 or size_download <= 0 or duration <= 0:
            logging.error("Invalid input values: size=%d, size_download=%d, duration=%f", size, size_download, duration)
            return

        # Add total size bytes
        self.ts_file_sizes.append(size)
        self.now_downloaded_size += size_download

    def capture_speed(self, interval: float = 1.0):
        """
        Capture the internet speed periodically and store the values in a deque.
        """
        def get_process_network_io(pid):
            process = psutil.Process(pid)
            io_counters = process.io_counters()
            return io_counters

        def convert_bytes_to_mbps(bytes):
            return (bytes * 8) / (1024 * 1024)

        pid = os.getpid()

        while True:
            old_value = get_process_network_io(pid)
            time.sleep(interval)
            new_value = get_process_network_io(pid)
            bytes_sent = new_value[2] - old_value[2]
            bytes_recv = new_value[3] - old_value[3]
            mbps_recv = convert_bytes_to_mbps(bytes_recv) / interval

            with self.lock:
                self.speeds.append(mbps_recv)

    def get_average_speed(self) -> float:
        """
        Calculate the average internet speed from the values in the deque.

        Returns:
            float: The average internet speed in Mbps.
        """
        with self.lock:
            if len(self.speeds) == 0:
                return 0.0
            return sum(self.speeds) / len(self.speeds)

    def calculate_total_size(self) -> str:
        """
        Calculate the total size of the files.

        Returns:
            str: The mean size of the files in a human-readable format.
        """
        try:
            if len(self.ts_file_sizes) == 0:
                raise ValueError("No file sizes available to calculate total size.")

            total_size = sum(self.ts_file_sizes)
            mean_size = total_size / len(self.ts_file_sizes)

            # Return formatted mean size
            return format_size(mean_size)
        
        except ZeroDivisionError as e:
            logging.error("Division by zero error occurred: %s", e)
            return "0B"
        
        except Exception as e:
            logging.error("An unexpected error occurred: %s", e)
            return "Error"
    
    def get_downloaded_size(self) -> str:
        """
        Get the total downloaded size formatted as a human-readable string.

        Returns:
            str: The total downloaded size as a human-readable string.
        """
        return format_size(self.now_downloaded_size)
    
    def update_progress_bar(self, total_downloaded: int, duration: float, progress_counter: tqdm) -> None:
        """
        Updates the progress bar with information about the TS segment download.

        Args:
            total_downloaded (int): The len of the content of the downloaded TS segment.
            duration (float): The duration of the segment download in seconds.
            progress_counter (tqdm): The tqdm object representing the progress bar.
        """
        # Add the size of the downloaded segment to the estimator
        self.add_ts_file(total_downloaded * self.total_segments, total_downloaded, duration)
                    
        # Get downloaded size and total estimated size
        downloaded_file_size_str = self.get_downloaded_size()                                 
        file_total_size = self.calculate_total_size()

        # Fix parameter for prefix
        number_file_downloaded = downloaded_file_size_str.split(' ')[0]
        number_file_total_size = file_total_size.split(' ')[0]
        units_file_downloaded = downloaded_file_size_str.split(' ')[1]
        units_file_total_size = file_total_size.split(' ')[1]
        average_internet_speed = self.get_average_speed() / 8 # Mbps -> MB\s

        # Update the progress bar's postfix
        if TQDM_USE_LARGE_BAR:
            progress_counter.set_postfix_str(
                f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded} {Colors.WHITE}< {Colors.GREEN}{number_file_total_size} {Colors.RED}{units_file_total_size} "
                f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed:.2f} {Colors.RED}MB/s"
            )
        else:
            progress_counter.set_postfix_str(
                f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded}{Colors.RED} {units_file_downloaded} "
                f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed:.2f} {Colors.RED}Mbps"
            )
