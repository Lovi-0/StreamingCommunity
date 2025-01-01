# 21.04.25

import os
import time
import logging
import threading
from collections import deque


# External libraries
import psutil
from tqdm import tqdm


# Internal utilities
from StreamingCommunity.Util.color import Colors
from StreamingCommunity.Util.os import internet_manager
from StreamingCommunity.Util._jsonConfig import config_manager


# Variable
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')


class M3U8_Ts_Estimator:
    def __init__(self, total_segments: int):
        """
        Initialize the M3U8_Ts_Estimator object.
        
        Parameters:
            - total_segments (int): Length of total segments to download.
        """
        self.ts_file_sizes = []
        self.now_downloaded_size = 0
        self.total_segments = total_segments
        self.lock = threading.Lock()
        self.speed = {"upload": "N/A", "download": "N/A"}
        self.process_pid = os.getpid()  # Get current process PID
        logging.debug(f"Initializing M3U8_Ts_Estimator with PID: {self.process_pid}")

        # Start the speed capture thread if TQDM_USE_LARGE_BAR is True
        if TQDM_USE_LARGE_BAR:
            logging.debug("TQDM_USE_LARGE_BAR is True, starting speed capture thread")
            self.speed_thread = threading.Thread(target=self.capture_speed, args=(1, self.process_pid))
            self.speed_thread.daemon = True
            self.speed_thread.start()

        else:
            logging.debug("TQDM_USE_LARGE_BAR is False, speed capture thread not started")

    def add_ts_file(self, size: int, size_download: int, duration: float):
        """Add a file size to the list of file sizes."""
        logging.debug(f"Adding ts file - size: {size}, download size: {size_download}, duration: {duration}")
        
        if size <= 0 or size_download <= 0 or duration <= 0:
            logging.error(f"Invalid input values: size={size}, size_download={size_download}, duration={duration}")
            return

        self.ts_file_sizes.append(size)
        self.now_downloaded_size += size_download
        logging.debug(f"Current total downloaded size: {self.now_downloaded_size}")

    def capture_speed(self, interval: float = 1, pid: int = None):
        """Capture the internet speed periodically."""
        logging.debug(f"Starting speed capture with interval {interval}s for PID: {pid}")
        
        def get_network_io(process=None):
            try:
                if process:

                    # For process-specific monitoring
                    connections = process.connections(kind='inet')
                    if connections:
                        io_counters = process.io_counters()
                        logging.debug(f"Process IO counters: {io_counters}")
                        return io_counters
                    
                    else:
                        logging.debug("No active internet connections found for process")
                        return None
                else:

                    # For system-wide monitoring
                    io_counters = psutil.net_io_counters()
                    logging.debug(f"System IO counters: {io_counters}")
                    return io_counters
                
            except Exception as e:
                logging.error(f"Error getting network IO: {str(e)}")
                return None

        try:
            process = psutil.Process(pid) if pid else None
            logging.debug(f"Monitoring process: {process}")

        except Exception as e:
            logging.error(f"Failed to get process with PID {pid}: {str(e)}")
            process = None

        last_upload = None
        last_download = None
        first_run = True
        
        # Buffer circolare per le ultime N misurazioni
        speed_buffer_size = 3
        speed_buffer = deque(maxlen=speed_buffer_size)

        while True:
            try:
                io_counters = get_network_io()
                
                if io_counters:
                    current_upload = io_counters.bytes_sent
                    current_download = io_counters.bytes_recv
                    
                    if not first_run and last_upload is not None and last_download is not None:

                        # Calcola la velocità istantanea
                        upload_speed = max(0, (current_upload - last_upload) / interval)
                        download_speed = max(0, (current_download - last_download) / interval)
                        
                        # Aggiungi al buffer
                        speed_buffer.append(download_speed)
                        
                        # Calcola la media mobile delle velocità
                        if len(speed_buffer) > 0:
                            avg_download_speed = sum(speed_buffer) / len(speed_buffer)
                            
                            if avg_download_speed > 0:
                                with self.lock:
                                    self.speed = {
                                        "upload": internet_manager.format_transfer_speed(upload_speed),
                                        "download": internet_manager.format_transfer_speed(avg_download_speed)
                                    }
                                    logging.debug(f"Updated speeds - Upload: {self.speed['upload']}, Download: {self.speed['download']}")
                    
                    last_upload = current_upload
                    last_download = current_download
                    first_run = False
                
                time.sleep(interval)
            except Exception as e:
                logging.error(f"Error in speed capture loop: {str(e)}")
                logging.exception("Full traceback:")
                logging.sleep(interval)

    def get_average_speed(self) -> list:
        """Calculate the average internet speed."""
        with self.lock:
            logging.debug(f"Current speed data: {self.speed}")
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
            return internet_manager.format_file_size(mean_size)

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
        return internet_manager.format_file_size(self.now_downloaded_size)
    
    def update_progress_bar(self, total_downloaded: int, duration: float, progress_counter: tqdm) -> None:
        """Updates the progress bar with download information."""
        try:
            self.add_ts_file(total_downloaded * self.total_segments, total_downloaded, duration)
            
            downloaded_file_size_str = self.get_downloaded_size()
            file_total_size = self.calculate_total_size()
            
            number_file_downloaded = downloaded_file_size_str.split(' ')[0]
            number_file_total_size = file_total_size.split(' ')[0]
            units_file_downloaded = downloaded_file_size_str.split(' ')[1]
            units_file_total_size = file_total_size.split(' ')[1]
            
            if TQDM_USE_LARGE_BAR:
                speed_data = self.get_average_speed()
                logging.debug(f"Speed data for progress bar: {speed_data}")
                
                if len(speed_data) >= 2:
                    average_internet_speed = speed_data[0]
                    average_internet_unit = speed_data[1]

                else:
                    logging.warning(f"Invalid speed data format: {speed_data}")
                    average_internet_speed = "N/A"
                    average_internet_unit = ""
                
                progress_str = (
                    f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded} {Colors.WHITE}< "
                    f"{Colors.GREEN}{number_file_total_size} {Colors.RED}{units_file_total_size} "
                    f"{Colors.WHITE}| {Colors.CYAN}{average_internet_speed} {Colors.RED}{average_internet_unit}"
                )
                
            else:
                progress_str = (
                    f"{Colors.WHITE}[ {Colors.GREEN}{number_file_downloaded} {Colors.WHITE}< "
                    f"{Colors.GREEN}{number_file_total_size} {Colors.RED}{units_file_total_size}"
                )
            
            progress_counter.set_postfix_str(progress_str)
            logging.debug(f"Updated progress bar: {progress_str}")
            
        except Exception as e:
            logging.error(f"Error updating progress bar: {str(e)}")