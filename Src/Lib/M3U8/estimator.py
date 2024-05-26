# 20.02.24

from collections import deque


# External libraries
from tqdm import tqdm


# Internal utilities
from Src.Util.color import Colors
from Src.Util.os import format_size


class M3U8_Ts_Estimator:
    def __init__(self, workers: int, total_segments: int):
        """
        Initialize the TSFileSizeCalculator object.

        Args:
            - workers (int): The number of workers using with ThreadPool.
            - total_segments (int): Len of total segments to download
        """
        self.ts_file_sizes = []
        self.now_downloaded_size = 0
        self.average_over = 5
        self.list_speeds = deque(maxlen=self.average_over)
        self.smoothed_speeds = []
        self.tqdm_workers = workers
        self.total_segments = total_segments

    def add_ts_file(self, size: int, size_download: int, duration: float):
        """
        Add a file size to the list of file sizes.

        Args:
            - size (float): The size of the ts file to be added.
            - size_download (int): Single size of the ts file.
            - duration (float): Time to download segment file.
        """
        self.ts_file_sizes.append(size)
        self.now_downloaded_size += size_download

        # Only for the start
        if len(self.smoothed_speeds) <= 3:
            size_download = size_download / self.tqdm_workers

        # Calculate mbps 
        speed_mbps = (size_download * 8) / (duration * 1_000_000)  * self.tqdm_workers
        self.list_speeds.append(speed_mbps)

        # Calculate moving average
        smoothed_speed = sum(self.list_speeds) / len(self.list_speeds)
        self.smoothed_speeds.append(smoothed_speed)

        # Update smooth speeds
        if len(self.smoothed_speeds) > self.average_over:
            self.smoothed_speeds.pop(0)

    def calculate_total_size(self) -> str:
        """
        Calculate the total size of the files.

        Returns:
            float: The mean size of the files in a human-readable format.
        """

        if len(self.ts_file_sizes) == 0:
            return 0

        total_size = sum(self.ts_file_sizes)
        mean_size = total_size / len(self.ts_file_sizes)

        # Return format mean
        return format_size(mean_size)
    
    def get_average_speed(self) -> float:
        """
        Calculate the average speed from a list of speeds and convert it to megabytes per second (MB/s).

        Returns:
            float: The average speed in megabytes per second (MB/s).
        """
        return (sum(self.smoothed_speeds) / len(self.smoothed_speeds)) / 10  # MB/s
    
    def get_downloaded_size(self) -> str:
        """
        Get the total downloaded size formatted as a human-readable string.

        Returns:
            str: The total downloaded size as a human-readable string.
        """
        return format_size(self.now_downloaded_size)
    
    def update_progress_bar(self, segment_content: bytes, duration: float, progress_counter: tqdm) -> None:
        """
        Updates the progress bar with information about the TS segment download.

        Args:
            segment_content (bytes): The content of the downloaded TS segment.
            duration (float): The duration of the segment download in seconds.
            progress_counter (tqdm): The tqdm object representing the progress bar.
        """
        total_downloaded = len(segment_content)

        # Add the size of the downloaded segment to the estimator
        self.add_ts_file(total_downloaded * self.total_segments, total_downloaded, duration)
                    
        # Get downloaded size and total estimated size
        downloaded_file_size_str = self.get_downloaded_size().split(' ')[0]                                    
        file_total_size = self.calculate_total_size()

        # Fix parameter for prefix
        number_file_total_size = file_total_size.split(' ')[0]
        units_file_total_size = file_total_size.split(' ')[1]
        average_internet_speed = self.get_average_speed()

        # Update the progress bar's postfix
        progress_counter.set_postfix_str(
            f"{Colors.WHITE}[ {Colors.GREEN}{downloaded_file_size_str} {Colors.WHITE}< {Colors.GREEN}{number_file_total_size} {Colors.RED}{units_file_total_size} "
            f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed:.2f} {Colors.RED}MB/s"
        )