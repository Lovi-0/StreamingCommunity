# 10.12.24

import requests, os, shutil
from zipfile import ZipFile
from io import BytesIO
from rich.console import Console

# Variable
console = Console()
local_path = os.path.join(".")

def move_content(source: str, destination: str) -> None:
    """
    Recursively moves content from source directory to destination directory.

    Args:
        source (str): Path to the source directory.
        destination (str): Path to the destination directory.

    Returns:
        None
    """
    os.makedirs(destination, exist_ok=True)
    for element in os.listdir(source):
        source_path = os.path.join(source, element)
        destination_path = os.path.join(destination, element)
        if os.path.isdir(source_path):
            move_content(source_path, destination_path)
        else:
            shutil.move(source_path, destination_path)

def delete_files_folders(main_directory_path: str, folders_to_exclude: list = [], files_to_exclude: list = []) -> None:
    """
    Deletes files and folders from the specified directory except those specified.

    Args:
        main_directory_path (str): Path to the main directory.
        folders_to_exclude (list): List of folder names to exclude from deletion.
        files_to_exclude (list): List of file names to exclude from deletion.

    Returns:
        None
    """
    for root, dirs, files in os.walk(main_directory_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            if name not in files_to_exclude:
                try:
                    os.remove(file_path)
                except:
                    pass
        for name in dirs:
            dir_path = os.path.join(root, name)
            if name not in folders_to_exclude:
                try:
                    os.rmdir(dir_path)
                except:
                    pass

def list_files_and_folders(directory: str, files_to_remove: list = []) -> None:
    """
    Lists files and folders in the specified directory and removes those specified.

    Args:
        directory (str): Path to the directory to list files and folders.
        files_to_remove (list): List of file names to remove.

    Returns:
        None
    """
    try:
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name in files_to_remove:
                    os.remove(file_path)
    except Exception as e:
        print(f"Error occurred: {e}")

def download_and_extract_latest_commit(author: str, repo_name: str, exclude_files: list) -> None:
    """
    Downloads and extracts the latest commit from a GitHub repository.

    Args:
        author (str): The username of the repository owner.
        repo_name (str): The name of the repository.
        exclude_files (list): List of file names to exclude from extraction.

    Returns:
        None
    """
    api_url = f'https://api.github.com/repos/{author}/{repo_name}/commits?per_page=1'
    response = requests.get(api_url)
    console.log("[green]Making a request to GitHub repository...")

    if response.ok:
        commit_info = response.json()[0]
        commit_sha = commit_info['sha']
        zipball_url = f'https://github.com/{author}/{repo_name}/archive/{commit_sha}.zip'
        console.log("[green]Getting zip file from repository...")
        response = requests.get(zipball_url)

        temp_path = os.path.join(os.path.dirname(os.getcwd()), 'temp_extracted')
        with ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(temp_path)
        console.log("[green]Extracting file ...")

        list_files_and_folders(temp_path, exclude_files)

        for item in os.listdir(temp_path):
            item_path = os.path.join(temp_path, item)
            destination_path = os.path.join(local_path, item)
            shutil.move(item_path, destination_path)

        shutil.rmtree(temp_path)
        new_folder_name = f"{repo_name}-{commit_sha}"
        move_content(new_folder_name, ".")
        shutil.rmtree(new_folder_name)
        console.log(f"[cyan]Latest commit downloaded and extracted successfully.")
    else:
        console.log(f"[red]Failed to fetch commit information. Status code: {response.status_code}")

def main_upload() -> None:
    """
    Main function to upload the latest changes from a GitHub repository.

    Returns:
        None
    """
    repository_owner = 'Ghost6446'
    repository_name = 'StreamingCommunity_api'

    cmd_insert = input("Are you sure you want to delete all files? (Only videos folder will remain) [yes/no]: ")

    if cmd_insert.lower() == "yes" or cmd_insert.lower() == "y":
        delete_files_folders(
            main_directory_path=".", 
            folders_to_exclude=["videos"],
            files_to_exclude=["upload.py", "config.json"]
        )
        download_and_extract_latest_commit(repository_owner, repository_name, ["config.json"])

main_upload()

# pyinstaller --onefile --add-data "./Src/upload/__version__.py;Src/upload" run.py
