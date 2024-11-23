# 23.06.24

import os
import sys
import time
import shutil
import logging


# Internal utilities
from StreamingCommunity.Src.Util.color import Colors
from StreamingCommunity.Src.Util.os import internet_manager
from StreamingCommunity.Src.Util._jsonConfig import config_manager


# External libraries
from tqdm import tqdm
from qbittorrent import Client


# Tor config
HOST = str(config_manager.get_dict('DEFAULT', 'config_qbit_tor')['host'])
PORT = str(config_manager.get_dict('DEFAULT', 'config_qbit_tor')['port'])
USERNAME = str(config_manager.get_dict('DEFAULT', 'config_qbit_tor')['user'])
PASSWORD = str(config_manager.get_dict('DEFAULT', 'config_qbit_tor')['pass'])

# Config
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')
REQUEST_VERIFY = config_manager.get_float('REQUESTS', 'verify_ssl')
REQUEST_TIMEOUT = config_manager.get_float('REQUESTS', 'timeout')



class TOR_downloader:
    def __init__(self):
        """
        Initializes the TorrentManager instance.

        Parameters:
            - host (str): IP address or hostname of the qBittorrent Web UI.
            - port (int): Port number of the qBittorrent Web UI.
            - username (str): Username for logging into qBittorrent.
            - password (str): Password for logging into qBittorrent.
        """
        try: 
            self.qb = Client(f'http://{HOST}:{PORT}/')
        except: 
            logging.error("Start qbitorrent first.")
        
        self.username = USERNAME
        self.password = PASSWORD
        self.logged_in = False
        self.save_path = None
        self.torrent_name = None

        self.login()

    def login(self):
        """
        Logs into the qBittorrent Web UI.
        """
        try:
            self.qb.login(self.username, self.password)
            self.logged_in = True
            logging.info("Successfully logged in to qBittorrent.")

        except Exception as e:
            logging.error(f"Failed to log in: {str(e)}")
            self.logged_in = False

    def add_magnet_link(self, magnet_link):
        """
        Adds a torrent via magnet link to qBittorrent.

        Parameters:
            - magnet_link (str): Magnet link of the torrent to be added.
        """
        try:
            self.qb.download_from_link(magnet_link)
            logging.info("Added magnet link to qBittorrent.")

            # Get the hash of the latest added torrent
            torrents = self.qb.torrents()
            if torrents:
                self.latest_torrent_hash = torrents[-1]['hash']
                logging.info(f"Latest torrent hash: {self.latest_torrent_hash}")

        except Exception as e:
            logging.error(f"Failed to add magnet link: {str(e)}")

    def start_download(self):
        """
        Starts downloading the latest added torrent and monitors progress.
        """    
        try:
            
            torrents = self.qb.torrents()
            if not torrents:
                logging.error("No torrents found.")
                return
            
            # Sleep to load magnet to qbit app
            time.sleep(10)
            latest_torrent = torrents[-1]
            torrent_hash = latest_torrent['hash']

            # Custom bar for mobile and pc
            if TQDM_USE_LARGE_BAR:
                bar_format = (
                    f"{Colors.YELLOW}[TOR] {Colors.WHITE}({Colors.CYAN}video{Colors.WHITE}): "
                    f"{Colors.RED}{{percentage:.2f}}% {Colors.MAGENTA}{{bar}} {Colors.WHITE}[ "
                    f"{Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"
                )
            else:
                bar_format = (
                    f"{Colors.YELLOW}Proc{Colors.WHITE}: "
                    f"{Colors.RED}{{percentage:.2f}}% {Colors.WHITE}| "
                    f"{Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"
                )

            progress_bar = tqdm(
                total=100,
                ascii='░▒█',
                bar_format=bar_format,
                unit_scale=True,
                unit_divisor=1024,
                mininterval=0.05
            )

            with progress_bar as pbar:
                while True:

                    # Get variable from qtorrent
                    torrent_info = self.qb.get_torrent(torrent_hash)
                    self.save_path = torrent_info['save_path']
                    self.torrent_name = torrent_info['name']

                    # Fetch important variable
                    pieces_have = torrent_info['pieces_have']
                    pieces_num = torrent_info['pieces_num']
                    progress = (pieces_have / pieces_num) * 100 if pieces_num else 0
                    pbar.n = progress

                    download_speed = torrent_info['dl_speed']
                    total_size = torrent_info['total_size']
                    downloaded_size = torrent_info['total_downloaded']

                    # Format variable
                    downloaded_size_str = internet_manager.format_file_size(downloaded_size)
                    downloaded_size = downloaded_size_str.split(' ')[0]

                    total_size_str = internet_manager.format_file_size(total_size)
                    total_size = total_size_str.split(' ')[0]
                    total_size_unit = total_size_str.split(' ')[1]

                    average_internet_str = internet_manager.format_transfer_speed(download_speed)
                    average_internet = average_internet_str.split(' ')[0]
                    average_internet_unit = average_internet_str.split(' ')[1]

                    # Update the progress bar's postfix
                    if TQDM_USE_LARGE_BAR:
                        pbar.set_postfix_str(
                            f"{Colors.WHITE}[ {Colors.GREEN}{downloaded_size} {Colors.WHITE}< {Colors.GREEN}{total_size} {Colors.RED}{total_size_unit} "
                            f"{Colors.WHITE}| {Colors.CYAN}{average_internet} {Colors.RED}{average_internet_unit}"
                        )
                    else:
                        pbar.set_postfix_str(
                            f"{Colors.WHITE}[ {Colors.GREEN}{downloaded_size}{Colors.RED} {total_size} "
                            f"{Colors.WHITE}| {Colors.CYAN}{average_internet} {Colors.RED}{average_internet_unit}"
                        )
                    
                    pbar.refresh()
                    time.sleep(0.2)

                    # Break at the end
                    if int(progress) == 100:
                        break

        except KeyboardInterrupt:
            logging.info("Download process interrupted.")

        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            sys.exit(0)

    def move_downloaded_files(self, destination=None):
        """
        Moves downloaded files of the latest torrent to another location.

        Parameters:
            - save_path (str): Current save path (output directory) of the torrent.
            - destination (str, optional): Destination directory to move files. If None, moves to current directory.

        Returns:
            - bool: True if files are moved successfully, False otherwise.
        """

        video_extensions = {'.mp4', '.mkv', 'avi'}
        time.sleep(2)
        
        # List directories in the save path
        dirs = [d for d in os.listdir(self.save_path) if os.path.isdir(os.path.join(self.save_path, d))]
        
        for dir_name in dirs:
            if self.torrent_name.split(" ")[0] in dir_name:
                dir_path = os.path.join(self.save_path, dir_name)

                # Ensure destination is set; if not, use current directory
                destination = destination or os.getcwd()

                # Move only video files
                for file_name in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file_name)
                    
                    # Check if it's a file and if it has a video extension
                    if os.path.isfile(file_path) and os.path.splitext(file_name)[1] in video_extensions:
                        shutil.move(file_path, os.path.join(destination, file_name))
                        logging.info(f"Moved file {file_name} to {destination}")

        time.sleep(2)
        self.qb.delete_permanently(self.qb.torrents()[-1]['hash'])
        return True
