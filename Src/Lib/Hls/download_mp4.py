# 09.06.24

import os
import sys
import logging


# External libraries
import requests
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

    if not os.path.exists(path):
        console.log("[cyan]Video [red]already exists.")
        sys.exit(0)


    # Make request to get content of video
    logging.info(f"Make request to fetch mp4 from: {url}")
    response = requests.get(url, stream=True, headers={'Referer': referer, 'user-agent': get_headers()}, verify=REQUEST_VERIFY, timeout=REQUEST_TIMEOUT)
    total = int(response.headers.get('content-length', 0))


    # Create bar format
    if TQDM_USE_LARGE_BAR:
        bar_format=f"{Colors.YELLOW}Downloading {Colors.WHITE}({add_desc}{Colors.WHITE}): {Colors.RED}{{percentage:.2f}}% {Colors.MAGENTA}{{bar}} {Colors.WHITE}[ {Colors.YELLOW}{{n_fmt}}{Colors.WHITE} / {Colors.RED}{{total_fmt}} {Colors.WHITE}] {Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}} {Colors.WHITE}| {Colors.YELLOW}{{rate_fmt}}{{postfix}} {Colors.WHITE}]"
    else:
        bar_format=f"{Colors.YELLOW}Proc{Colors.WHITE}: {Colors.RED}{{percentage:.2f}}% {Colors.WHITE}| {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"

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
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


    # Get summary
    console.print(Panel(
                f"[bold green]Download completed![/bold green]\n"
                f"File size: [bold red]{format_size(os.path.getsize(path))}[/bold red]\n"
                f"Duration: [bold]{print_duration_table(path, show=False)}[/bold]", 
            title=f"{os.path.basename(path.replace('.mp4', ''))}", border_style="green"))
