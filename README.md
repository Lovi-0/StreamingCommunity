<p align="center">
    <img src="./Src/Assets/min_logo.png">
</p>


This repository provide a simple script designed to facilitate the downloading of films and series from a popular streaming community platform. The script allows users to download individual films, entire series, or specific episodes, providing a seamless experience for content consumers.

## Join us 🌟
You can chat, help improve this repo, or just hang around for some fun in the **Git_StreamingCommunity** Discord [Server](https://discord.com/invite/8vV68UGRc7)

# Table of Contents

* [INSTALLATION](#installation)
  * [Automatic Installation](#automatic-installation)
    * [Usage](#usage-automatic)
    * [Supported OSs for Automatic Installation](#automatic-installation-os)
  * [Manual Installation](#manual-installation)
    * [Requirement](#requirement)
    * [Usage](#usage-manual)
    * [Win 7](https://github.com/Ghost6446/StreamingCommunity_api/wiki/Installation#win-7)
    * [Termux](https://github.com/Ghost6446/StreamingCommunity_api/wiki/Termux) 
  * [Update](#update)
* [CONFIGURATION](#configuration)
* [DOCKER](#docker)
* [TUTORIAL](#tutorial)
* [TO DO](#to-do)

# INSTALLATION

## Automatic Installation
<a id="automatic-installation-os"></a>
### Supported OSs for Automatic Installation 💿
- Supported ✔️
- Not tested ⏳
- Not supported ❌

| OS                  |       Automatic Installation Support       |
|:--------------------|:--------------------:|
| Windows 10/11       |          ✔️          |
| Windows 7           |          ❌          |
| Debian Linux        |          ✔️          |
| Arch Linux          |          ✔️          |
| CentOS Stream 9     |          ✔️          |
| FreeBSD             |          ⏳           |
| MacOS               |          ✔️          |
| Termux              |          ❌          |

### Installation ⚙️
Run the following command inside the main directory:
#### On Windows:
```powershell
.\win_install.bat
```

#### On Linux/MacOS/BSD:
```bash
sudo chmod +x unix_install.sh && ./unix_install.sh
```

<a id="usage-automatic"></a>
### Usage 📚

Run the script with the following command:
#### On Windows:
```powershell
python .\run.py
```
or
```powershell
source .venv/bin/activate && python run.py && deactivate
```

#### On Linux/MacOS/BSD:
```bash
./run.py
```

## Manual Installation
<a id="requirement"></a>
### Requirement 📋

Make sure you have the following prerequisites installed on your system:

* [python](https://www.python.org/downloads/) > 3.8
* [ffmpeg](https://www.gyan.dev/ffmpeg/builds/)
* [openssl](https://www.openssl.org) or [pycryptodome](https://pypi.org/project/pycryptodome/)

### Installation ⚙️

Install the required Python libraries using the following command:

```
pip install -r requirements.txt
```

<a id="usage-manual"></a>
### Usage 📚

Run the script with the following command:

#### On Windows:

```powershell
python run.py
```

#### On Linux/MacOS:

```bash
python3 run.py
```


## Update

Keep your script up to date with the latest features by running:

#### On Windows:

```powershell
python update_version.py
```

#### On Linux/MacOS:

```bash
python3 update_version.py
```

<a id="configuration"></a>
## Configuration ⚙️

You can change some behaviors by tweaking the configuration file.

<details>
  <summary><strong>DEFAULT</strong></summary>

  * **debug**: Enables or disables debug mode.
    - **Default Value**: `false`

  * **root_path**: Path where the script will add movies and TV series folders (see [Path Examples](#Path-examples)).
    - **Default Value**: `Video`

  * **map_episode_name**: Mapping to choose the name of all episodes of TV Shows (see [Episode Name Usage](#Episode-name-usage)).
    - **Default Value**: `%(tv_name)_S%(season)E%(episode)_%(episode_name)`

  * **not_close**: When activated, prevents the script from closing after its initial execution, allowing it to restart automatically after completing the first run.
    - **Default Value**: `false`

</details>

<details>
  <summary><strong>REQUESTS</strong></summary>

  * **timeout**: The timeout value for requests.
    - **Default Value**: `10`

  * **verify_ssl**: Whether to verify SSL certificates.
    - **Default Value**: `false`

  * **proxy**: To use proxy create a file with name list_proxy.txt and copy ip and port like "122.114.232.137:8080". They need to be http 

</details>

<details>
  <summary><strong>M3U8_DOWNLOAD</strong></summary>

  * **tdqm_workers**: The number of workers that will cooperate to download .ts files. **A high value may slow down your PC**
    - **Default Value**: `30`

  * **tqdm_use_large_bar**: Whether to use large progress bars during downloads (Downloading %desc: %percentage:.2f %bar %elapsed < %remaining %postfix
    - **Default Value**: `true`
    - **Example Value**: `false` with Proc: %percentage:.2f %remaining %postfix

  * **download_video**: Whether to download video streams.
    - **Default Value**: `true`

  * **download_audio**: Whether to download audio streams.
    - **Default Value**: `true`

  * **download_sub**: Whether to download subtitle streams.
    - **Default Value**: `true`

  * **specific_list_audio**: A list of specific audio languages to download.
    - **Example Value**: `['ita']`

  * **specific_list_subtitles**: A list of specific subtitle languages to download.
    - **Example Value**: `['ara', 'baq', 'cat', 'chi', 'cze', 'dan', 'dut', 'eng', 'fil', 'fin', 'forced-ita', 'fre', 'ger', 'glg', 'gre', 'heb', 'hin', 'hun', 'ind', 'ita', 'jpn', 'kan', 'kor', 'mal', 'may', 'nob', 'nor', 'pol', 'por', 'rum', 'rus', 'spa', 'swe', 'tam', 'tel', 'tha', 'tur', 'ukr', 'vie']`

  * **cleanup_tmp_folder**: Upon final conversion, ensures the removal of all unformatted audio, video tracks, and subtitles from the temporary folder, thereby maintaining cleanliness and efficiency.
    - **Default Value**: `false`

</details>

<details>
  <summary><strong>M3U8_PARSER</strong></summary>

  * **force_resolution**: Forces the use of a specific resolution. `-1` means no forced resolution.
    - **Default Value**: `-1`
    - **Example Value**: `1080`

</details>

> [!IMPORTANT]
> If you're on **Windows** you'll need to use double back slash. On Linux/MacOS, one slash is fine.

#### Path examples:

* Windows: `C:\\MyLibrary\\Folder` or `\\\\MyServer\\MyLibrary` (if you want to use a network folder).
* Linux/MacOS: `Desktop/MyLibrary/Folder`

#### Episode name usage:

You can choose different vars:

* `%(tv_name)` : Is the name of TV Show
* `%(season)` : Is the number of the season
* `%(episode)` : Is the number of the episode
* `%(episode_name)` : Is the name of the episode

> NOTE: You don't need to add .mp4 at the end

<a id="docker"></a>
## Docker 🐳

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

<a id="tutorial"></a>
## Tutorial 📖

[win]("https://www.youtube.com/watch?v=mZGqK4wdN-k")
[linux]("https://www.youtube.com/watch?v=0qUNXPE_mTg")

<a id="to-do"></a>
## To do 📝
- GUI
- Website api
- Add other site
