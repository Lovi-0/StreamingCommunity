# 07.04.24

import platform
import os
import logging

# Winreg only work for windows
if platform.system() == "Windows":

    # Winreg only work for windows
    import winreg

    # Define Windows registry key for user environment variables
    env_keys = winreg.HKEY_CURRENT_USER, "Environment"

else:
    env_keys = None


def get_env(name: str) -> str:
    """
    Retrieve the value of the specified environment variable from the Windows registry.
    
    Args:
        name (str): The name of the environment variable to retrieve.
    
    Returns:
        str: The value of the specified environment variable.
    """
    try:
        with winreg.OpenKey(*env_keys, 0, winreg.KEY_READ) as key:
            return winreg.QueryValueEx(key, name)[0]
            
    except FileNotFoundError:
        return ""


def set_env_path(dir: str) -> None:
    """
    Add a directory to the user's PATH environment variable.

    Args:
        dir (str): The directory to add to the PATH environment variable.
    """
    user_path = get_env("Path")

    if dir not in user_path:
        new_path = user_path + os.pathsep + dir

        try:
            with winreg.OpenKey(*env_keys, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            logging.info(f"Added {dir} to PATH.")
            print("Path set successfully.")

        except Exception as e:
            logging.error(f"Failed to set PATH: {e}")
            print("Failed to set PATH.")

    else:
        print("Directory already exists in the Path.")


def remove_from_path(dir) -> None:
    """
    Remove a directory from the user's PATH environment variable.

    Args:
        dir (str): The directory to remove from the PATH environment variable.
    """
    user_path = get_env("Path")

    if dir in user_path:
        new_path = user_path.replace(dir + os.pathsep, "").replace(os.pathsep + dir, "")

        try:
            with winreg.OpenKey(*env_keys, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            logging.info(f"Removed {dir} from PATH.")
            print("Directory removed from Path.")

        except Exception as e:
            logging.error(f"Failed to remove directory from PATH: {e}")
            print("Failed to remove directory from Path.")

    else:
        print("Directory does not exist in the Path.")


def backup_path():
    """
    Backup the original state of the PATH environment variable.
    """
    original_path = get_env("Path")

    try:

        # Create backup dir
        script_dir = os.path.join(os.path.expanduser("~"), "Backup")
        os.makedirs(script_dir, exist_ok=True)

        backup_file = os.path.join(script_dir, "path_backup.txt")

        # Check if backup file exist
        if not os.path.exists(backup_file):

            with open(backup_file, "w") as f:
                for path in original_path.split("\n"):
                    if len(path) > 3:
                        f.write(f"{path}; \n")

            logging.info("Backup of PATH variable created.")
            print("Backup of PATH variable created.")

    except Exception as e:
        logging.error(f"Failed to create backup of PATH variable: {e}")
        print(f"Failed to create backup of PATH variable: {e}")


def restore_path():
    """
    Restore the original state of the PATH environment variable.
    """
    try:
        backup_file = "path_backup.txt"

        if os.path.isfile(backup_file):
            with open(backup_file, "r") as f:
                new_path = f.read()
                with winreg.OpenKey(*env_keys, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)

            logging.info("Restored original PATH variable.")
            print("Restored original PATH variable.")
            os.remove(backup_file)

        else:
            logging.warning("No backup file found.")
            print("No backup file found.")
    except Exception as e:
        logging.error(f"Failed to restore PATH variable: {e}")
        print("Failed to restore PATH variable.")
