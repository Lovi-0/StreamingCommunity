# 20.02.24

import threading
import logging
from collections import deque


# External libraries
from tqdm import tqdm


# Internal utilities
from Src.Util.color import Colors
from Src.Util.os import format_size
from Src.Util._jsonConfig import config_manager



# Variable
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')


class M3U8_Ts_Estimator:
    def __init__(self, total_segments: int):
        self.ts_file_sizes = []
        self.now_downloaded_size = 0
        self.average_over = 5
        self.list_speeds = deque(maxlen=self.average_over)
        self.total_segments = total_segments
        self.last_segment_duration = 1
        self.last_segment_size = 0

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

        # Calibrazione dinamica del tempo
        self.last_segment_duration = duration

        # Considerazione della variazione di dimensione del segmento
        self.last_segment_size = size_download

        # Calcolo velocità
        try:
            speed_mbps = (size_download * 8) / (duration * 1024 * 1024)

        except ZeroDivisionError as e:
            logging.error("Division by zero error while calculating speed: %s", e)
            return

        self.ts_file_sizes.append(size)
        self.now_downloaded_size += size_download
        self.list_speeds.append(speed_mbps)

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
    
    def get_average_speed(self) -> float:
        """
        Calculate the average speed from a list of speeds and convert it to megabytes per second (MB/s).

        Returns:
            float: The average speed in megabytes per second (MB/s).
        """

        # Smooth the speeds for better accuracy using the window defined by average_over
        smoothed_speed = sum(self.list_speeds) / min(len(self.list_speeds), self.average_over)
        predicted_speed = smoothed_speed * (self.last_segment_size / (1024 * 1024)) / self.last_segment_duration

        # Convert to mb/s
        return predicted_speed  / 8 
    
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
        average_internet_speed = self.get_average_speed()

        # Update the progress bar's postfix
        if TQDM_USE_LARGE_BAR:
            progress_counter.set_postfix_str(
                f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded} {Colors.WHITE}< {Colors.GREEN}{number_file_total_size} {Colors.RED}{units_file_total_size} "
                f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed:.2f} {Colors.RED}MB/s"
            )

        else:
            progress_counter.set_postfix_str(
                f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded}{Colors.RED} {units_file_downloaded} "
                f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed:.2f} {Colors.RED}MB/s"
            )