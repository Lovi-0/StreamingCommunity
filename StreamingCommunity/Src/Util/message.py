# 3.12.23

import os
import platform


# Internal utilities
from StreamingCommunity.Src.Util.console import console
from StreamingCommunity.Src.Util._jsonConfig import config_manager


# Variable
CLEAN = config_manager.get_bool('DEFAULT', 'clean_console')
SHOW = config_manager.get_bool('DEFAULT', 'show_message')


def start_message():
    """
    Display a start message.
    """

    msg = r'''

   _____ _                            _                _____                                      _ _         
  / ____| |                          (_)              / ____|                                    (_) |        
 | (___ | |_ _ __ ___  __ _ _ __ ___  _ _ __   __ _  | |     ___  _ __ ___  _ __ ___  _   _ _ __  _| |_ _   _ 
  \___ \| __| '__/ _ \/ _` | '_ ` _ \| | '_ \ / _` | | |    / _ \| '_ ` _ \| '_ ` _ \| | | | '_ \| | __| | | |
  ____) | |_| | |  __/ (_| | | | | | | | | | | (_| | | |___| (_) | | | | | | | | | | | |_| | | | | | |_| |_| |
 |_____/ \__|_|  \___|\__,_|_| |_| |_|_|_| |_|\__, |  \_____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|_|\__|\__, |
                                               __/ |                                                     __/ |
                                              |___/                                                     |___/ 

    '''

    if CLEAN: 
        if platform.system() == 'Windows':
            os.system("cls")
        else:
            os.system("clear")
    
    if SHOW:
        console.print(f"[bold yellow]{msg}")
        console.print(f"[magenta]Created by: Lovi\n")

        row = "-" * console.width
        console.print(f"[yellow]{row} \n")
