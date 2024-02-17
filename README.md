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
```python
python run.py
```

## Auto Update
Keep your script up to date with the latest features by running:
```python
python update.py
```

## Features
- Download Single Film: Easily download individual movies with a simple command.

- Download Specific Episodes or Entire Series: Seamlessly retrieve specific episodes or entire series using intuitive commands. Specify a range of episodes with square brackets notation, e.g., [5-7], or download all episodes with an asterisk (*).

- Download Subtitles: Automatically fetch subtitles if available for downloaded content. (Note: To disable this feature, navigate to ".\Src\Lib\FFmpeg\my_m3u8" and change 'DOWNLOAD_SUB' to False in the configuration file.)

- Sync Audio and Video: Ensure perfect synchronization between audio and video during the download process for an enhanced viewing experience.

## Tutorial
For a detailed walkthrough, refer to the [video tutorial](https://www.youtube.com/watch?v=Ok7hQCgxqLg&ab_channel=Nothing)

## Authors
- [@Ghost6446](https://www.github.com/Ghost6446)
