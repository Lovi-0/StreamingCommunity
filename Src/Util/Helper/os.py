# 24.01.24

# Import
import shutil, os

def remove_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            print(f"Error removing folder '{folder_path}': {e}")