# 29.02.24

from Src.Util.os import format_size

class TSFileSizeCalculator:
    def __init__(self):
        """
        Initialize the TSFileSizeCalculator object.

        Args:
            num_segments (int): The number of segments.
        """
        self.ts_file_sizes = []

    def add_ts_file_size(self, size: int):
        """
        Add a file size to the list of file sizes.

        Args:
            size (float): The size of the ts file to be added.
        """
        self.ts_file_sizes.append(size)

    def calculate_total_size(self):
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