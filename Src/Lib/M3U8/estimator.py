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
from Src.Util.os import format_file_size, format_transfer_speed
from Src.Util._jsonConfig import config_manager


# Variable
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')


class M3U8_Ts_Estimator:
    def __init__(self, total_segments: int):
        """
        Initialize the TSFileSizeCalculator object.

        Parameters:
            - total_segments (int): Len of total segments to download
        """
        self.ts_file_sizes = []
        self.now_downloaded_size = 0
        self.total_segments = total_segments
        self.lock = threading.Lock()
        self.speed = 0
        self.speed_thread = threading.Thread(target=self.capture_speed)
        self.speed_thread.daemon = True
        self.speed_thread.start()

    def add_ts_file(self, size: int, size_download: int, duration: float):
        """
        Add a file size to the list of file sizes.

        Parameters:
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

    def capture_speed(self, interval: float = 1):
        """
        Capture the internet speed periodically and store the values in a deque.
        """
        def get_network_io():
            io_counters = psutil.net_io_counters()
            return io_counters

        # Get proc id
        pid = os.getpid()
        
        while True:

            # Get value
            old_value = get_network_io()
            time.sleep(interval)
            new_value = get_network_io()

            with self.lock:
                upload_speed = (new_value.bytes_sent - old_value.bytes_sent) / interval
                download_speed = (new_value.bytes_recv - old_value.bytes_recv) / interval
                
                self.speed = ({
                    "upload": format_transfer_speed(upload_speed),
                    "download": format_transfer_speed(download_speed)
                })

                old_value = new_value
            

    def get_average_speed(self) -> float:
        """
        Calculate the average internet speed from the values in the deque.

        Returns:
            float: The average internet speed in Mbps.
        """
        with self.lock:
            return self.speed['download'].split(" ")

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
            return format_file_size(mean_size)
        
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
        return format_file_size(self.now_downloaded_size)
    
    def update_progress_bar(self, total_downloaded: int, duration: float, progress_counter: tqdm) -> None:
        """
        Updates the progress bar with information about the TS segment download.

        Parameters:
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

        average_internet_speed = self.get_average_speed()[0]
        average_internet_unit = self.get_average_speed()[1]

        # Update the progress bar's postfix
        if TQDM_USE_LARGE_BAR:
            progress_counter.set_postfix_str(
                f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded} {Colors.WHITE}< {Colors.GREEN}{number_file_total_size} {Colors.RED}{units_file_total_size} "
                f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed} {Colors.RED}{average_internet_unit}"
            )
        else:
            progress_counter.set_postfix_str(
                f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded}{Colors.RED} {units_file_downloaded} "
                f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed} {Colors.RED}{average_internet_unit}"
            )
