# 09.06.24

import os
import sys
import logging


# External libraries
import httpx
from tqdm import tqdm


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util.color import Colors
from Src.Util.console import console, Panel
from Src.Util._jsonConfig import config_manager
from Src.Util.os import format_size


# Logic class
from ..FFmpeg import print_duration_table


# Config
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')
REQUEST_VERIFY = config_manager.get_float('REQUESTS', 'verify_ssl')
REQUEST_TIMEOUT = config_manager.get_float('REQUESTS', 'timeout')



def MP4_downloader(url: str, path: str, referer: str, add_desc: str):

    # Make request to get content of video
    logging.info(f"Make request to fetch mp4 from: {url}")
    headers = {'Referer': referer, 'user-agent': get_headers()}
    
    with httpx.Client(verify=REQUEST_VERIFY, timeout=REQUEST_TIMEOUT) as client:
        with client.stream("GET", url, headers=headers, timeout=99) as response:
            total = int(response.headers.get('content-length', 0))

            # Create bar format
            if TQDM_USE_LARGE_BAR:
                bar_format = (f"{Colors.YELLOW}Downloading {Colors.WHITE}({add_desc}{Colors.WHITE}): "
                              f"{Colors.RED}{{percentage:.2f}}% {Colors.MAGENTA}{{bar}} {Colors.WHITE}[ "
                              f"{Colors.YELLOW}{{n_fmt}}{Colors.WHITE} / {Colors.RED}{{total_fmt}} {Colors.WHITE}] "
                              f"{Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}} {Colors.WHITE}| "
                              f"{Colors.YELLOW}{{rate_fmt}}{{postfix}} {Colors.WHITE}]")
            else:
                bar_format = (f"{Colors.YELLOW}Proc{Colors.WHITE}: {Colors.RED}{{percentage:.2f}}% "
                              f"{Colors.WHITE}| {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]")

            # Create progress bar
            progress_bar = tqdm(
                total=total,
                unit='iB',
                ascii='░▒█',
                bar_format=bar_format,
                unit_scale=True,
                unit_divisor=1024
            )

            # Download file
            with open(path, 'wb') as file, progress_bar as bar:
                for chunk in response.iter_bytes(chunk_size=1024):
                    if chunk:
                        size = file.write(chunk)
                        bar.update(size)

    # Get summary
    console.print(Panel(
        f"[bold green]Download completed![/bold green]\n"
        f"File size: [bold red]{format_size(os.path.getsize(path))}[/bold red]\n"
        f"Duration: [bold]{print_duration_table(path, show=False)}[/bold]", 
        title=f"{os.path.basename(path.replace('.mp4', ''))}", 
        border_style="green"
    ))