# 10.12.24

# General imports
import requests, os, shutil
from zipfile import ZipFile
from io import BytesIO
from rich.console import Console

# Variable
console = Console()
local_path = os.path.join(".")

def move_content(source: str, destination: str) :
    os.makedirs(destination, exist_ok=True)

    for element in os.listdir(source):
        source_path = os.path.join(source, element)
        destination_path = os.path.join(destination, element)

        if os.path.isdir(source_path):
            move_content(source_path, destination_path)
        
        else:
            shutil.move(source_path, destination_path)

def keep_specific_items(directory: str, keep_folder: str, keep_file: str):

    try:
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise ValueError(f"Error: '{directory}' is not a valid directory.")

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and item != keep_folder:
                shutil.rmtree(item_path)
            elif os.path.isfile(item_path) and item != keep_file:
                os.remove(item_path)

    except PermissionError as pe:
        print(f"PermissionError: {pe}. Check permissions and try running the script with admin privileges.")

    except Exception as e:
        print(f"Error: {e}")

def download_and_extract_latest_commit(author: str, repo_name: str):

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

def main_upload():
    repository_owner = 'Ghost6446'
    repository_name = 'StreamingCommunity_api'

    cmd_insert = input("Are you sure you want to delete all files? (Only videos folder will remain) [yes/no]: ")

    if cmd_insert == "yes":
        keep_specific_items(".", "videos", "upload.py")
        download_and_extract_latest_commit(repository_owner, repository_name)

main_upload()
