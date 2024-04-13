# 3.12.23 -> 19.07.24

import os
import platform


# External libraries
from Src.Util.console import console


# Internal utilities
from .config import config_manager


# Variable
CLEAN = config_manager.get_bool('DEFAULT', 'clean_console')
SHOW = config_manager.get_bool('DEFAULT', 'show_message')


def get_os_system():
    """
    This function returns the name of the operating system.
    """
    os_system = platform.system()
    return os_system


def start_message(switch = False):
    """
    Display a start message.

    This function prints a formatted start message, including a title and creator information.
    """

    msg = """

   _____ _                            _                _____                                      _ _         
  / ____| |                          (_)              / ____|                                    (_) |        
 | (___ | |_ _ __ ___  __ _ _ __ ___  _ _ __   __ _  | |     ___  _ __ ___  _ __ ___  _   _ _ __  _| |_ _   _ 
  \___ \| __| '__/ _ \/ _` | '_ ` _ \| | '_ \ / _` | | |    / _ \| '_ ` _ \| '_ ` _ \| | | | '_ \| | __| | | |
  ____) | |_| | |  __/ (_| | | | | | | | | | | (_| | | |___| (_) | | | | | | | | | | | |_| | | | | | |_| |_| |
 |_____/ \__|_|  \___|\__,_|_| |_| |_|_|_| |_|\__, |  \_____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|_|\__|\__, |
                                               __/ |                                                     __/ |
                                              |___/                                                     |___/ 

    """

    if switch:
        msg = """
        
     _          _                            _ _         
    / \   _ __ (_)_ __ ___   ___ _   _ _ __ (_) |_ _   _ 
   / _ \ | '_ \| | '_ ` _ \ / _ \ | | | '_ \| | __| | | |
  / ___ \| | | | | | | | | |  __/ |_| | | | | | |_| |_| |
 /_/   \_\_| |_|_|_| |_| |_|\___|\__,_|_| |_|_|\__|\__, |
                                                   |___/ 

    """

    if CLEAN: 
        if get_os_system() == 'Windows':
            os.system("cls")
        else:
            os.system("clear")
    
    if SHOW:
        
        console.print(f"[bold yellow]{msg}")
        console.print(f"[magenta]Created by: Ghost6446\n")

        row = "-" * console.width
        console.print(f"[yellow]{row} \n")