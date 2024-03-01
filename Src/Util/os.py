# 24.01.24

# Import
import shutil, os, time

def remove_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            print(f"Error removing folder '{folder_path}': {e}")


def remove_file(file_path):
    if os.path.exists(file_path):
        time.sleep(1)

        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error removing file '{file_path}': {e}")
    else:
        print(f"File '{file_path}' does not exist.")