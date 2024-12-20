# 23.06.24

import os
import re
import sys
import time
import shutil
import psutil
import logging


# Internal utilities
from StreamingCommunity.Util.color import Colors
from StreamingCommunity.Util.os import internet_manager
from StreamingCommunity.Util.console import console
from StreamingCommunity.Util._jsonConfig import config_manager


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
            console.print(f"[cyan]Connect to: [green]{HOST}:{PORT}")
            self.qb = Client(f'http://{HOST}:{PORT}/')
        except: 
            logging.error("Start qbitorrent first.")
            sys.exit(0)
        
        self.username = USERNAME
        self.password = PASSWORD
        self.latest_torrent_hash = None
        self.output_file = None
        self.file_name = None

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

    def delete_magnet(self, torrent_info):

        if (int(torrent_info.get('dl_speed')) == 0 and 
            int(torrent_info.get('peers')) == 0 and 
            int(torrent_info.get('seeds')) == 0):
            
            # Elimina il torrent appena aggiunto
            console.print(f"[bold red]⚠️ Torrent non scaricabile. Rimozione in corso...[/bold red]")
            
            try:
                # Rimuovi il torrent
                self.qb.delete_permanently(torrent_info['hash'])

            except Exception as delete_error:
                logging.error(f"Errore durante la rimozione del torrent: {delete_error}")
            
            # Resetta l'ultimo hash
            self.latest_torrent_hash = None

    def add_magnet_link(self, magnet_link):
        """
        Aggiunge un magnet link e recupera le informazioni dettagliate.

        Args:
            magnet_link (str): Magnet link da aggiungere
        
        Returns:
            dict: Informazioni del torrent aggiunto, o None se fallisce
        """

        # Estrai l'hash dal magnet link
        magnet_hash_match = re.search(r'urn:btih:([0-9a-fA-F]+)', magnet_link)
        
        if not magnet_hash_match:
            raise ValueError("Hash del magnet link non trovato")
        
        magnet_hash = magnet_hash_match.group(1).lower()
        
        # Estrai il nome del file dal magnet link (se presente)
        name_match = re.search(r'dn=([^&]+)', magnet_link)
        torrent_name = name_match.group(1).replace('+', ' ') if name_match else "Nome non disponibile"
        
        # Salva il timestamp prima di aggiungere il torrent
        before_add_time = time.time()
        
        # Aggiungi il magnet link
        console.print(f"[cyan]Aggiunta magnet link[/cyan]: [red]{magnet_link}")
        self.qb.download_from_link(magnet_link)
        
        # Aspetta un attimo per essere sicuri che il torrent sia stato aggiunto
        time.sleep(1)
        
        # Cerca il torrent
        torrents = self.qb.torrents()
        matching_torrents = [
            t for t in torrents 
            if (t['hash'].lower() == magnet_hash) or (t.get('added_on', 0) > before_add_time)
        ]
        
        if not matching_torrents:
            raise ValueError("Nessun torrent corrispondente trovato")
        
        # Prendi il primo torrent corrispondente
        torrent_info = matching_torrents[0]
        
        # Formatta e stampa le informazioni
        console.print("\n[bold green]🔗 Dettagli Torrent Aggiunto:[/bold green]")
        console.print(f"[yellow]Nome:[/yellow] {torrent_info.get('name', torrent_name)}")
        console.print(f"[yellow]Hash:[/yellow] {torrent_info['hash']}")
        console.print(f"[yellow]Dimensione:[/yellow] {internet_manager.format_file_size(torrent_info.get('size'))}")
        print()

        # Salva l'hash per usi successivi e il path
        self.latest_torrent_hash = torrent_info['hash']
        self.output_file = torrent_info['content_path']
        self.file_name = torrent_info['name']

        # Controlla che sia possibile il download
        time.sleep(5)
        self.delete_magnet(self.qb.get_torrent(self.latest_torrent_hash))
        
        return torrent_info

    def start_download(self):
        """
        Starts downloading the latest added torrent and monitors progress.
        """    
        if self.latest_torrent_hash is not None:
            try:
            
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
                        torrent_info = self.qb.get_torrent(self.latest_torrent_hash)
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

    def is_file_in_use(self, file_path: str) -> bool:
        """Check if a file is in use by any process."""
        for proc in psutil.process_iter(['open_files']):
            try:
                if any(file_path == f.path for f in proc.info['open_files'] or []):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    def move_downloaded_files(self, destination: str):
        """
        Moves downloaded files of the latest torrent to another location.

        Parameters:
            - destination (str): Destination directory to move files.

        Returns:
            - bool: True if files are moved successfully, False otherwise.
        """
        console.print(f"[cyan]Destination folder: [red]{destination}")
        
        try:

            # Ensure the file is not in use
            timeout = 3
            elapsed = 0
            while self.is_file_in_use(self.output_file) and elapsed < timeout:
                time.sleep(1)
                elapsed += 1
            
            if elapsed == timeout:
                raise Exception(f"File '{self.output_file}' is in use and could not be moved.")

            # Ensure destination directory exists
            os.makedirs(destination, exist_ok=True)

            # Perform the move operation
            try:
                shutil.move(self.output_file, destination)

            except OSError as e:
                if e.errno == 17:  # Cross-disk move error
                    # Perform copy and delete manually
                    shutil.copy2(self.output_file, destination)
                    os.remove(self.output_file)
                else:
                    raise

            # Delete the torrent data
            #self.qb.delete_permanently(self.qb.torrents()[-1]['hash'])
            return True

        except Exception as e:
            print(f"Error moving file: {e}")
            return False