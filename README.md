<p align="center">
	<img src="Src/Assets/min_logo.png" style="max-width: 55%;" alt="video working" />
</p>

## Streaming community downloader
<p align="center">
	<img src="Src/Assets/run.gif" style="max-width: 55%;" alt="video working" />
</p>

## Overview.
This repository provide a simple script designed to facilitate the downloading of films and series from a popular streaming community platform. The script allows users to download individual films, entire series, or specific episodes, providing a seamless experience for content consumers.

## Requirement
Make sure you have the following prerequisites installed on your system:

* python > [3.11](https://www.python.org/downloads/)
* ffmpeg [win](https://www.gyan.dev/ffmpeg/builds/)

## Installation library
Install the required Python libraries using the following command:
```bash
pip install -r requirements.txt
```

## Usage
Run the script with the following command:
```powershell
python run.py
```

## Auto Update
Keep your script up to date with the latest features by running:
```powershell
python update.py
```

## Features
- Download Single Film: Easily download individual movies with a simple command.

- Download Specific Episodes or Entire Series: Seamlessly retrieve specific episodes or entire series using intuitive commands. Specify a range of episodes with square brackets notation, e.g., [5-7], or download all episodes with an asterisk (*).

- Download Subtitles: Automatically fetch subtitles if available for downloaded content. (Note: To disable this feature, see [Configuration](#configuration))

- Sync Audio and Video: Ensure perfect synchronization between audio and video during the download process for an enhanced viewing experience.

## Configuration

You can change some behaviors by tweaking the configuration file.

```json
{
  "root_path": "videos",
  "movies_folder_name": "Movies",
  "series_folder_name": "Series",
  "download_subtitles": true,
  "download_default_language": true,
  "selected_language": "English",
  "max_worker": 20
}
```
#### Options
| Key                       | Default Value | Description                                                                              | Value Example            |
|---------------------------|---------------|------------------------------------------------------------------------------------------|--------------------------|
| root_path                 | videos        | *Path where the script will add movies and tv series folders. Do not put trailing slash. | media/streamingcommunity |
| movies_folder_name        | Movies        | The folder name where all the movies will be placed. Do not put trailing slash.          | downloaded-movies        |
| series_folder_name        | Series        | The folder name where all the TV Series will be placed. Do not put trailing slash.       | mytvseries               |
| download_subtitles        | true          | Whether or not you want all the found subtitles to be downloaded.                        | false                    |
| download_default_language | true          | Whether or not you want to download only the default Italian audio language.             | false                    |
| selected_language         | English       | If `"download_default_language"` is `False` the script will download this language       | French                   |
| max_worker                | 20            | How many workers will cooperate to download .ts file (High value may slow down your pc)  | 30                       |

> [!IMPORTANT]
> If you're on **Windows** you'll need to use double black slashes. Otherwise, one slash is fine.

Path examples:

* Windows: `C:\\MyLibrary\\Folder` or `\\\\MyServer\\MyLibrary` (if you want to use a network folder).

* Linux/MacOS: `Desktop/MyLibrary/Folder`

## Tutorial
For a detailed walkthrough, refer to the [video tutorial](https://www.youtube.com/watch?v=Ok7hQCgxqLg&ab_channel=Nothing)

## Authors
- [@Ghost6446](https://www.github.com/Ghost6446)
