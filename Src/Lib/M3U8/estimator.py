# 20.02.24

from collections import deque

# Internal utilities
from Src.Util.os import format_size


class M3U8_Ts_Estimator:
    def __init__(self, workers: int):
        """
        Initialize the TSFileSizeCalculator object.

        Args:
            - workers (int): The number of workers using with ThreadPool.
        """
        self.ts_file_sizes = []
        self.now_downloaded_size = 0
        self.average_over = 5
        self.list_speeds = deque(maxlen=self.average_over)
        self.smoothed_speeds = []
        self.tqdm_workers = workers

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