# 5.01.24 -> 7.01.24 -> 17.02.24

# Class import
from Src.Util.console import console
from Src.Util.headers import get_headers
from Src.Util.config import config
from Src.Lib.FFmpeg.util import print_duration_table

# Import
from m3u8 import M3U8 as M3U8_Lib
from tqdm.rich import tqdm
import requests, os, ffmpeg, sys, warnings, shutil, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Disable warning
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="cryptography")

# Variable
MAX_WORKER = config['max_worker']
DOWNLOAD_PATH = config['root_path']
DOWNLOAD_SUB = config['download_subtitles']
DOWNLOAD_DEFAULT_LANGUAGE = config['download_default_language']
SELECTED_LANGUAGE = config['selected_language']
failed_segments = []


# [ main class ]
class Decryption():
    def __init__(self, key):
        self.iv = None
        self.key = key

    def parse_key(self, raw_iv):
        self.iv = bytes.fromhex(raw_iv.replace("0x", ""))

    def decrypt_ts(self, encrypted_data):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data

class M3U8_Parser:
    def __init__(self):
        self.segments = []
        self.video_playlist = []
        self.keys = []
        self.subtitle_playlist = []     # No vvt ma url a vvt
        self.subtitle = []              # Url a vvt
        self.audio_ts = []

    def parse_data(self, m3u8_content):
        """Extract all info present in m3u8 content"""

        try:
            m3u8_obj = M3U8_Lib(m3u8_content)

            for playlist in m3u8_obj.playlists:
                self.video_playlist.append({"uri": playlist.uri})
                self.stream_infos = ({
                    "bandwidth": playlist.stream_info.bandwidth,
                    "codecs": playlist.stream_info.codecs,
                    "resolution": playlist.stream_info.resolution
                })

            for key in m3u8_obj.keys:
                if key is not None:
                    self.keys = ({
                        "method": key.method,
                        "uri": key.uri,
                        "iv": key.iv
                    })

            for media in m3u8_obj.media:
                if media.type == "SUBTITLES":
                    self.subtitle_playlist.append({
                        "type": media.type,
                        "name": media.name,
                        "default": media.default,
                        "language": media.language,
                        "uri": media.uri
                    })
                else:
                    self.audio_ts.append({
                        "type": media.type,
                        "name": media.name,
                        "default": media.default,
                        "language": media.language,
                        "uri": media.uri
                    })

            for segment in m3u8_obj.segments:
                if "vtt" not in segment.uri:
                    self.segments.append(segment.uri)
                else:
                    self.subtitle.append(segment.uri)

        except Exception as e:
            print(f"Error parsing M3U8 content: {e}")

    def get_best_quality(self):

        if self.video_playlist:
            return self.video_playlist[0].get('uri')
        else:
            print("No video playlist found")
            return None
        
    def download_subtitle(self, subtitle_path, content_name):
        """Download all subtitle if present"""

        path = subtitle_path

        if self.subtitle_playlist:
            for sub_info in self.subtitle_playlist:
                name_language = sub_info.get("language")

                os.makedirs(path, exist_ok=True)
                console.log(f"[green]Downloading subtitle: [red]{name_language}")
                req_sub_content = requests.get(sub_info.get("uri"))

                sub_parse = M3U8_Parser()
                sub_parse.parse_data(req_sub_content.text)
                url_subtitle = sub_parse.subtitle[0]

                if "forced" in name_language.lower():
                    name_language = name_language.lower().replace("forced", "").strip()
                    name_language = name_language.lower().replace("-", "").strip()
                    subtitle_name = f"{content_name}.{name_language}.forced.vtt"
                else:
                    subtitle_name = f"{content_name}.{name_language}.vtt"

                # Save vtt to path
                open(
                    os.path.join(path, subtitle_name), "wb"
                ).write(requests.get(url_subtitle).content)

        else:
            console.log("[red]No subtitle found")

    def get_track_audio(self, language_name):   # Ex. English
        """Return url of audio eng audio playlist if present"""

        if self.audio_ts:
            console.log(f"[cyan]Found {len(self.audio_ts)}, playlist with audio")

            if language_name is not None:
                for obj_audio in self.audio_ts:
                    if obj_audio.get("name") == language_name:
                        return obj_audio.get("uri")

            return None
        
        else:
            console.log("[red]Couldn't find any playlist with audio")

class M3U8_Segments:
    def __init__(self, url, key=None):
        self.url = url
        self.key = key
        if key is not None:
            self.decription = Decryption(key)

        self.temp_folder = os.path.join("tmp", "segments")
        os.makedirs(self.temp_folder, exist_ok=True)

        self.progress_timeout = 10
        self.max_retry = 3

    def parse_data(self, m3u8_content):
         
        # Parse index m3u8
        m3u8_parser = M3U8_Parser()
        m3u8_parser.parse_data(m3u8_content)
        
        # Add decryption iv if present
        if self.key is not None and m3u8_parser.keys:
            self.decription.parse_key(m3u8_parser.keys.get("iv"))

        # Add all segments
        self.segments = m3u8_parser.segments

    def get_info(self):
        """Make req to index m3u8"""

        response = requests.get(self.url, headers={'user-agent': get_headers()})

        if response.ok:
            self.parse_data(response.text)

            if len(self.segments) == 0:
                console.log("[red]Couldn't find any segments to download, retry")
                sys.exit(0)

        else:
            console.log(f"[red]Wrong m3u8, error: {response.status_code}")
            sys.exit(0)

    def get_req_ts(self, ts_url):
        """Single req to a ts file to get content"""

        url_number = self.segments.index(ts_url)

        is_valid = True
        for failde_seg in failed_segments:
            if str(failde_seg) in ts_url:
                is_valid = False
                break

        if is_valid:

            try:
                response = requests.get(ts_url, headers={'user-agent': get_headers()}, timeout=10)

                if response.status_code == 200:
                    return response.content
                else:
                    failed_segments.append(str(url_number))
                    return None
                
            except Exception as e:
                failed_segments.append(str(url_number))
                return None
        
        else:
            return None

    def save_ts(self, index, progress_counter, quit_event):
        """Save ts file and decrypt if there is iv present in decryption class"""
        
        ts_url = self.segments[index]
        ts_filename = os.path.join(self.temp_folder, f"{index}.ts")

        if not os.path.exists(ts_filename):
            ts_content = self.get_req_ts(ts_url)

            if ts_content is not None:
                with open(ts_filename, "wb") as ts_file:
                    if self.key and self.decription.iv:
                        decrypted_data = self.decription.decrypt_ts(ts_content)
                        ts_file.write(decrypted_data)
                    else:
                        ts_file.write(ts_content)
        
        progress_counter.update(1)
          
    def download_ts(self):
        progress_counter = tqdm(total=len(self.segments), unit="bytes", desc="[yellow]Download")
        
        quit_event = threading.Event()
        timeout_occurred = False

        timer_thread = threading.Thread(target=self.timer, args=(progress_counter, quit_event, lambda: timeout_occurred))
        timer_thread.start()

        try:
            with ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
                futures = []
                for index in range(len(self.segments)):
                    if timeout_occurred:
                        break
                    future = executor.submit(self.save_ts, index, progress_counter, quit_event)
                    futures.append(future)
                    
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")

        finally:
            progress_counter.close()
            quit_event.set()
            timer_thread.join()


    def timer(self, progress_counter, quit_event, timeout_checker):
        start_time = time.time()
        last_count = 0

        while not quit_event.is_set():
            current_count = progress_counter.n

            if current_count != last_count:
                start_time = time.time()
                last_count = current_count

            elapsed_time = time.time() - start_time
            if elapsed_time > self.progress_timeout:
                console.log(f"[red]No progress for {self.progress_timeout} seconds.")
                console.log("[red]Breaking ThreadPoolExecutor...")
                timeout_checker()
                quit_event.set()
                break

            time.sleep(1)

        progress_counter.refresh()

    def join(self, output_filename):
        """Join all segments file to a mp4 file name"""

        file_list_path = os.path.join('file_list.txt')
        ts_files = [f for f in os.listdir(self.temp_folder) if f.endswith(".ts")]

        def extract_number(file_name):
            return int(''.join(filter(str.isdigit, file_name)))
        ts_files.sort(key=extract_number)

        if len(ts_files) == 0:
            console.log("[red]Couldn't find any segments to join, retry")
            sys.exit(0)

        with open(file_list_path, 'w') as f:
            for ts_file in ts_files:
                relative_path = os.path.relpath(os.path.join(self.temp_folder, ts_file))
                f.write(f"file '{relative_path}'\n")

        #console.log("[cyan]Joining all files...")
        try:
            ffmpeg.input(file_list_path, format='concat', safe=0).output(output_filename, map_metadata='-1', c='copy', loglevel='error').run()
        except ffmpeg.Error as e:
            console.log(f"[red]Error saving MP4: {e.stdout}")
            
        #console.log(f"[cyan]Clean ...")
        os.remove(file_list_path)
        shutil.rmtree("tmp", ignore_errors=True)

class M3U8_Downloader:
    def __init__(self, m3u8_url, m3u8_audio = None, key=None, output_filename="output.mp4"):
        self.m3u8_url = m3u8_url
        self.m3u8_audio = m3u8_audio
        self.key = key
        self.video_path = output_filename
        self.audio_path = os.path.join(DOWNLOAD_PATH, "audio.mp4")

    def start(self):
        video_m3u8 = M3U8_Segments(self.m3u8_url, self.key)
        console.log("[purple]Downloading video ts")
        video_m3u8.get_info()
        video_m3u8.download_ts()
        video_m3u8.join(self.video_path)
        print_duration_table(self.video_path)

        if self.m3u8_audio is not None:
            audio_m3u8 = M3U8_Segments(self.m3u8_audio, self.key)
            console.log("[purple]Downloading audio ts")
            audio_m3u8.get_info()
            audio_m3u8.download_ts()
            audio_m3u8.join(self.audio_path)
            print_duration_table(self.audio_path)

            self.join_audio()

        if os.path.exists(f"{self.video_path}.mp4"):
            os.renames(f"{self.video_path}.mp4", self.video_path)
        
    def join_audio(self):
        console.log("[purple]Join audio and video")

        try:
            video_stream = ffmpeg.input(self.video_path)
            audio_stream = ffmpeg.input(self.audio_path)

            process = (
                ffmpeg.output(
                    video_stream,
                    audio_stream,
                    self.video_path + ".mp4",
                    vcodec="copy",
                    acodec="copy",
                    loglevel='error'
                )
                .global_args(
                    '-map', '0:v:0', 
                    '-map', '1:a:0', 
                    '-shortest', '-strict', 
                    'experimental')
                .run()
            )

            console.print("[green]Merge completed successfully.")

        except ffmpeg.Error as e:
            print("ffmpeg error:", e)
        
        os.remove(self.video_path)
        os.remove(self.audio_path)


# [ main function ]
def df_make_req(url):
    response = requests.get(url)

    if response.ok:
        return response.text
    else:
        console.log(f"[red]Wrong url, error: {response.status_code}")
        sys.exit(0)

def download_subtitle(url, name_language):
    path = os.path.join(DOWNLOAD_PATH, "subtitle")
    os.makedirs(path, exist_ok=True)

    console.log(f"[green]Downloading subtitle: [red]{name_language}")
    open(os.path.join(path, name_language + ".vtt"), "wb").write(requests.get(url).content)

def download_m3u8(
        m3u8_playlist=None, 
        m3u8_index = None, 
        m3u8_audio=None, 
        m3u8_subtitle=None, 
        key=None, 
        output_filename=os.path.join(DOWNLOAD_PATH, "output.mp4"), 
        log=False, 
        subtitle_folder="subtitles", 
        content_name=""
    ):

    m3u8_audio_url=None
    # m3u8_playlist never use in this version

    key = bytes.fromhex(key) if key is not None else key

    if m3u8_audio is not None:
        m3u8_audio_obj = None
        if DOWNLOAD_DEFAULT_LANGUAGE:
            m3u8_audio_obj = next((audioobj for audioobj in m3u8_audio if audioobj.get("default", False)), None) or m3u8_audio[0]
        elif SELECTED_LANGUAGE:
            m3u8_audio_obj = next((audioobj for audioobj in m3u8_audio if audioobj["lang"] == SELECTED_LANGUAGE), None)
        if m3u8_audio_obj is None:
            console.log("[red]Cant find a valid m3u8 audio")
            sys.exit(0)
        m3u8_audio_url = m3u8_audio_obj["url"]
        console.log(f"[green]Select language => [purple]{m3u8_audio_obj['lang']}")

    if m3u8_subtitle != None:

        parse_class_m3u8_sub = M3U8_Parser()

        # Parse directly m3u8 content pass if present
        if "#EXTM3U" not in m3u8_subtitle: 
            parse_class_m3u8_sub.parse_data(df_make_req(m3u8_subtitle))
        else: 
            parse_class_m3u8_sub.parse_data(m3u8_subtitle)

        # Download subtitle if present ( normally in m3u8 playlist )
        if DOWNLOAD_SUB:
            parse_class_m3u8_sub.download_subtitle(subtitle_path=subtitle_folder, content_name=content_name)

    # Download m3u8 index, with segments
    path = os.path.dirname(output_filename)
    os.makedirs(path, exist_ok=True)

    if log: 
        console.log(f"[green]Download m3u8 from index [white]=> [purple]{m3u8_index}")
    M3U8_Downloader(m3u8_index, m3u8_audio_url, key=key, output_filename=output_filename).start()
