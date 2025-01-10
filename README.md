<p align="center">
  <img src="https://i.ibb.co/PFnjvBc/immagine-2024-12-26-180318047.png" alt="Project Logo" width="700"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/streamingcommunity">
    <img src="https://img.shields.io/pypi/v/streamingcommunity?logo=pypi&labelColor=555555&style=for-the-badge" alt="PyPI"/>
  </a>
  <a href="https://www.paypal.com/donate/?hosted_button_id=UXTWMT8P6HE2C">
    <img src="https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="Donate"/>
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-GPL_3.0-blue.svg?style=for-the-badge" alt="License"/>
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity/commits">
    <img src="https://img.shields.io/github/commit-activity/m/Lovi-0/StreamingCommunity?label=commits&style=for-the-badge" alt="Commits"/>
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity/commits">
    <img src="https://img.shields.io/github/last-commit/Lovi-0/StreamingCommunity/main?label=&style=for-the-badge&display_timestamp=committer" alt="Last Commit"/>
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/streamingcommunity">
    <img src="https://img.shields.io/pypi/dm/streamingcommunity?style=for-the-badge" alt="PyPI Downloads"/>
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity/network/members">
    <img src="https://img.shields.io/github/forks/Lovi-0/StreamingCommunity?style=for-the-badge" alt="Forks"/>
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity">
    <img src="https://img.shields.io/github/languages/code-size/Lovi-0/StreamingCommunity?style=for-the-badge" alt="Code Size"/>
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity">
    <img src="https://img.shields.io/github/repo-size/Lovi-0/StreamingCommunity?style=for-the-badge" alt="Repo Size"/>
  </a>
</p>

# 📋 Table of Contents

- 🌐 [Website available](#website-status)
- 🛠️ [Installation](#installation)
    - 📦 [PyPI Installation](#1-pypi-installation)
    - 🔄 [Automatic Installation](#2-automatic-installation)
    - 📝 [Manual Installation](#3-manual-installation)
        - 💻 [Win 7](https://github.com/Ghost6446/StreamingCommunity_api/wiki/Installation#win-7)
        - 📱 [Termux](https://github.com/Ghost6446/StreamingCommunity_api/wiki/Termux)
- ⚙️ [Configuration](#configuration)
    - 🔧 [Default](#default-settings)
    - 📩 [Request](#requests-settings)
    - 📥 [Download](#m3u8_download-settings)
    - 🔍 [Parser](#m3u8_parser-settings)
- 🐳 [Docker](#docker)
- 🎓 [Tutorial](#tutorials)
- 📝 [To do](#to-do)
- 💬 [Support](#support)
- 🤝 [Contribute](#contributing)
- ⚠️ [Disclaimer](#disclaimer)
- ⚡ [Contributors](#contributors)  

# Installation

<p align="center">
  <a href="https://github.com/Lovi-0/StreamingCommunity/releases/latest/download/StreamingCommunity.exe">
    <img src="https://img.shields.io/badge/-Windows_x64-blue.svg?style=for-the-badge&logo=windows" alt="Windows">
  </a>
  <a href="https://pypi.org/project/StreamingCommunity">
    <img src="https://img.shields.io/badge/-PyPI-blue.svg?logo=pypi&labelColor=555555&style=for-the-badge" alt="PyPI">
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity/releases/latest/download/StreamingCommunity.zip">
    <img src="https://img.shields.io/badge/-Source_tar-green.svg?style=for-the-badge" alt="Source Tarball">
  </a>
  <a href="https://github.com/Lovi-0/StreamingCommunity/releases">
    <img src="https://img.shields.io/badge/-All_Versions-lightgrey.svg?style=for-the-badge" alt="All Versions">
  </a>
</p>


## 1. PyPI Installation

Install directly from PyPI:

```bash
pip install StreamingCommunity
```

### Creating a Run Script

Create `run_streaming.py`:

```python
from StreamingCommunity.run import main

if __name__ == "__main__":
    main()
```

Run the script:
```bash
python run_streaming.py
```

## Updating via PyPI

```bash
pip install --upgrade StreamingCommunity
```

## 2. Automatic Installation

### Supported Operating Systems 💿

| OS              | Automatic Installation Support |
|:----------------|:------------------------------:|
| Windows 10/11   |              ✔️              |
| Windows 7       |              ❌              |
| Debian Linux    |              ✔️              |
| Arch Linux      |              ✔️              |
| CentOS Stream 9 |              ✔️              |
| FreeBSD         |              ⏳              |
| MacOS           |              ✔️              |
| Termux          |              ❌              |

### Installation Steps

#### On Windows:

```powershell
.\Installer\win_install.bat
```

#### On Linux/MacOS/BSD:

```bash
sudo chmod +x Installer/unix_install.sh && ./Installer/unix_install.sh
```

### Usage

#### On Windows:

```powershell
python .\test_run.py
```

or

```powershell
source .venv/bin/activate && python test_run.py && deactivate
```

#### On Linux/MacOS/BSD:

```bash
./test_run.py
```

## 3. Manual Installation

### Requirements 📋

Prerequisites:
* [Python](https://www.python.org/downloads/) > 3.8
* [FFmpeg](https://www.gyan.dev/ffmpeg/builds/)

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Usage

#### On Windows:

```powershell
python test_run.py
```

#### On Linux/MacOS:

```bash
python3 test_run.py
```

## Update

Keep your script up to date with the latest features by running:

### On Windows:

```powershell
python update.py
```

### On Linux/MacOS:

```bash
python3 update.py
```

<br>

# Configuration

You can change some behaviors by tweaking the configuration file.

The configuration file is divided into several main sections:

## DEFAULT Settings

```json
{
    "root_path": "Video",
    "movie_folder_name": "Movie",
    "serie_folder_name": "TV",
    "map_episode_name": "%(tv_name)_S%(season)E%(episode)_%(episode_name)",
    "add_siteName": false,
    "disable_searchDomain": false,
    "not_close": false
}
```

- `root_path`: Directory where all videos will be saved
  
  ### Path examples:
  * Windows: `C:\\MyLibrary\\Folder` or `\\\\MyServer\\MyLibrary` (if you want to use a network folder)
  * Linux/MacOS: `Desktop/MyLibrary/Folder`
    `<br/><br/>`

- `movie_folder_name`: The name of the subdirectory where movies will be stored.
- `serie_folder_name`: The name of the subdirectory where TV series will be stored.

- `map_episode_name`: Template for TV series episode filenames

  ### Episode name usage:

  You can choose different vars:


  * `%(tv_name)` : Is the name of TV Show
  * `%(season)` : Is the number of the season
  * `%(episode)` : Is the number of the episode
  * `%(episode_name)` : Is the name of the episode
    `<br/><br/>`
    
- `add_siteName`: If set to true, appends the site_name to the root path before the movie and serie folders.
- `disable_searchDomain`: If set to true, disables the search for a new domain for all sites.
- `not_close`: If set to true, keeps the program running after the download is complete.


    ### qBittorrent Configuration

    ```json
    {
        "config_qbit_tor": {
            "host": "192.168.1.59",
            "port": "8080",
            "user": "admin",
            "pass": "adminadmin"
        }
    }
    ```

    To enable qBittorrent integration, follow the setup guide [here](https://github.com/lgallard/qBittorrent-Controller/wiki/How-to-enable-the-qBittorrent-Web-UI).


## REQUESTS Settings

```json
{
    "timeout": 20,
    "max_retry": 3
}
```

- `timeout`: Maximum timeout (in seconds) for each request
- `max_retry`: Number of retry attempts per segment during M3U8 index download


## M3U8_DOWNLOAD Settings

```json
{
    "tqdm_delay": 0.01,
    "tqdm_use_large_bar": true,
    "default_video_workser": 12,
    "default_audio_workser": 12,
    "cleanup_tmp_folder": true
}
```

- `tqdm_delay`: Delay between progress bar updates
- `tqdm_use_large_bar`: Use detailed progress bar (recommended for desktop) set to false for mobile
- `default_video_workser`: Number of threads for video download
- `default_audio_workser`: Number of threads for audio download
- `cleanup_tmp_folder`: Remove temporary .ts files after download

> [!IMPORTANT]
> Set `tqdm_use_large_bar` to `false` when using Termux or terminals with limited width to prevent network monitoring issues



### Language Settings

The following codes can be used for `specific_list_audio` and `specific_list_subtitles`:

```
ara - Arabic       eng - English      ita - Italian     por - Portuguese
baq - Basque       fil - Filipino     jpn - Japanese    rum - Romanian
cat - Catalan      fin - Finnish      kan - Kannada     rus - Russian
chi - Chinese      fre - French       kor - Korean      spa - Spanish
cze - Czech        ger - German       mal - Malayalam   swe - Swedish
dan - Danish       glg - Galician     may - Malay       tam - Tamil
dut - Dutch        gre - Greek        nob - Norw. Bokm  tel - Telugu
                   heb - Hebrew       nor - Norwegian    tha - Thai
forced-ita         hin - Hindi        pol - Polish      tur - Turkish
                   hun - Hungarian                       ukr - Ukrainian
                   ind - Indonesian                      vie - Vietnamese
```

> [!IMPORTANT]
> Language code availability may vary by site. Some platforms might:
>
> - Use different language codes
> - Support only a subset of these languages
> - Offer additional languages not listed here
>
> Check the specific site's available options if downloads fail.

> [!TIP]
> You can configure multiple languages by adding them to the lists:
>
> ```json
> "specific_list_audio": ["ita", "eng", "spa"],
> "specific_list_subtitles": ["ita", "eng", "spa"]
> ```

## M3U8_PARSER Settings

```json
{
    "force_resolution": -1,
    "get_only_link": false
}
```

- `force_resolution`: Force specific resolution (-1 for best available, or specify 1080, 720, 360)
- `get_only_link`: Return M3U8 playlist/index URL instead of downloading


# COMMAND

- Download a specific season by entering its number.
  *  **Example:** `1` will download *Season 1* only.

-  Use the wildcard `*` to download every available season.
   * **Example:** `*` will download all seasons in the series.

- Specify a range of seasons using a hyphen `-`.
   * **Example:** `1-2` will download *Seasons 1 and 2*.

- Enter a season number followed by `-*` to download from that season to the end.
  * **Example:** `3-*` will download from *Season 3* to the final season.


# Docker

You can run the script in a docker container, to build the image just run

```
docker build -t streaming-community-api .
```

and to run it use

```
docker run -it -p 8000:8000 streaming-community-api
```

By default the videos will be saved in `/app/Video` inside the container, if you want to to save them in your machine instead of the container just run

```
docker run -it -p 8000:8000 -v /path/to/download:/app/Video streaming-community-api
```

### Docker quick setup with Make

Inside the Makefile (install `make`) are already configured two commands to build and run the container:

```
make build-container

# set your download directory as ENV variable
make LOCAL_DIR=/path/to/download run-container
```

The `run-container` command mounts also the `config.json` file, so any change to the configuration file is reflected immediately without having to rebuild the image.

# Website Status 

| Website            | Status |
|:-------------------|:------:|
| [1337xx](https://1337xx.to/) |   ✅   |
| [Altadefinizione](https://altadefinizione.prof/) |   ✅   |
| [AnimeUnity](https://animeunity.so/) |   ✅   |
| [Ilcorsaronero](https://ilcorsaronero.link/) |   ✅   |
| [CB01New](https://cb01new.sbs/) |   ✅   |
| [DDLStreamItaly](https://ddlstreamitaly.co/) |   ✅   |
| [GuardaSerie](https://guardaserie.academy/) |   ✅   |
| [MostraGuarda](https://mostraguarda.stream/) |   ✅   |
| [StreamingCommunity](https://streamingcommunity.prof/) |   ✅   |


# Tutorials 

- [Windows Tutorial](https://www.youtube.com/watch?v=mZGqK4wdN-k)
- [Linux Tutorial](https://www.youtube.com/watch?v=0qUNXPE_mTg)
- [Pypy Tutorial](https://www.youtube.com/watch?v=C6m9ZKOK0p4)
- [Compiled .exe Tutorial](https://www.youtube.com/watch?v=pm4lqsxkTVo)

# To Do 

- Finish [website API](https://github.com/Lovi-0/StreamingCommunity/tree/test_gui_1)

# Contributing

Contributions are welcome! Steps:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request


# Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## Contributors

<a href="https://github.com/Lovi-0/StreamingCommunity/graphs/contributors" alt="View Contributors">
  <img src="https://contrib.rocks/image?repo=Lovi-0/StreamingCommunity&max=1000&columns=10" alt="Contributors" />
</a>
