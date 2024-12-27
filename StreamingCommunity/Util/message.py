# 3.12.23

import os
import platform

# Internal utilities
from StreamingCommunity.Util.console import console
from StreamingCommunity.Util._jsonConfig import config_manager

# Variable
CLEAN = config_manager.get_bool('DEFAULT', 'clean_console')
SHOW = config_manager.get_bool('DEFAULT', 'show_message')


def create_italian_flag_colored_text(text: str) -> str:
    """Create text divided into three sections with Italian flag colors, splitting each line at two spaces."""
    
    # Split the text into lines
    lines = text.splitlines()

    colored_lines = []

    for line in lines:
        # Split each line into parts using two spaces as a delimiter
        parts = line.split("       ")
        
        # Ensure there are exactly 3 parts (add empty strings if necessary)
        parts += [''] * (4 - len(parts))

        # Apply flag colors to the parts
        green_part = f"[green]{parts[0]}[/]"
        white_part = f"[white]{parts[1]}[/]"
        red_part = f"[red]{parts[2]}[/]"

        # Reassemble the colored line
        colored_line = green_part + white_part + red_part
        colored_lines.append(colored_line)

    # Join all colored lines back into a single string
    return "\n".join(colored_lines)

def start_message():
    """Display a stylized start message in the console."""
    
    msg = r'''
    ██╗      ██████╗ ██╗   ██╗██╗        ██╗  ██╗        ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗██╗███╗   ██╗ ██████╗
    ██║     ██╔═══██╗██║   ██║██║        ╚██╗██╔╝        ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔════╝
    ██║     ██║   ██║██║   ██║██║         ╚███╔╝         ███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║██║██╔██╗ ██║██║  ███╗
    ██║     ██║   ██║╚██╗ ██╔╝██║         ██╔██╗         ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║██║██║╚██╗██║██║   ██║
    ███████╗╚██████╔╝ ╚████╔╝ ██║        ██╔╝ ██╗        ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝
    ╚══════╝ ╚═════╝   ╚═══╝  ╚═╝        ╚═╝  ╚═╝        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    '''.rstrip()

    colored_msg = create_italian_flag_colored_text(msg)

    if CLEAN: 
        os.system("cls" if platform.system() == 'Windows' else "clear")
    
    if SHOW:
        console.print(colored_msg)

        # Print a decorative separator line using asterisks
        separator = "_" * (console.width - 2)  # Ridotto di 2 per il padding
        console.print(f"[yellow]{separator}[/yellow]\n")
