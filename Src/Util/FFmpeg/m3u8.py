# 5.01.24 -> 7.01.24

# Class import
from Src.Util.Helper.console import console, config_logger
from Src.Util.Helper.headers import get_headers
from Src.Util.FFmpeg.util import print_duration_table

# Import
import requests, re,  os, ffmpeg, time, sys, warnings, logging, shutil, subprocess
from tqdm.rich import tqdm
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Disable warning
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="cryptography")

# Variable
os.makedirs("videos", exist_ok=True)
DOWNLOAD_WORKERS = 30


# [ main class ]
class Decryption():
    def __init__(self, key):
        self.iv = None
        self.key = key

    def decode_ext_x_key(self, key_str):
        logging.debug(f"String to decode: {key_str}")
        key_str = key_str.replace('"', '').lstrip("#EXT-X-KEY:")
        v_list = re.findall(r"[^,=]+", key_str)
        key_map = {v_list[i]: v_list[i+1] for i in range(0, len(v_list), 2)}
        logging.debug(f"Output string: {key_map}")
        return key_map
    
    def parse_key(self, raw_iv):
        self.iv = bytes.fromhex(raw_iv.replace("0x", ""))

    def decrypt_ts(self, encrypted_data):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data

class M3U8():
    def __init__(self, url, key=None):
        self.url = url
        self.key = bytes.fromhex(key) if key is not None else key
        self.temp_folder = "tmp"
        os.makedirs(self.temp_folder, exist_ok=True)

    def parse_data(self, m3u8_content):
        self.decription = Decryption(self.key)
        self.segments = []
        base_url = self.url.rstrip(self.url.split("/")[-1])
        lines = m3u8_content.split('\n')

        for i in range(len(lines)):
            line = str(lines[i])

            if line.startswith("#EXT-X-KEY:"):
                x_key_dict = self.decription.decode_ext_x_key(line)
                self.decription.parse_key(x_key_dict['IV'])

            if line.startswith("#EXTINF"):
                ts_url = lines[i+1]

                if not ts_url.startswith("http"):
                    ts_url = base_url + ts_url

                logging.debug(f"Add to segment: {ts_url}")
                self.segments.append(ts_url)

    def get_info(self):
        self.max_retry = 3
        response = requests.get(self.url, headers={'user-agent': get_headers()})

        if response.ok:
            self.parse_data(response.text)
            console.log(f"[red]Ts segments find [white]=> [yellow]{len(self.segments)}")
        else:
            console.log("[red]Wrong m3u8 url")
            sys.exit(0)

    def get_req_ts(self, ts_url):

        try:
            response = requests.get(ts_url, headers={'user-agent': get_headers()})

            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed: {ts_url}, with error: {response.status_code}")
                self.segments.remove(ts_url)
                logging.error(f"Failed download: {ts_url}")
                return None
            
        except Exception as e:
            print(f"Failed: {ts_url}, with error: {e}")
            self.segments.remove(ts_url)
            logging.error(f"Failed download: {ts_url}")
            return None
        
    def save_ts(self, index):
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
          
    def download_ts(self):
        with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as executor:
            list(tqdm(executor.map(self.save_ts, range(len(self.segments)) ), total=len(self.segments), unit="bytes", unit_scale=True, unit_divisor=1024, desc="[yellow]Download"))

    def join(self, output_filename):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_list_path = os.path.join(current_dir, 'file_list.txt')

        ts_files = [f for f in os.listdir(self.temp_folder) if f.endswith(".ts")]
        def extract_number(file_name):
            return int(''.join(filter(str.isdigit, file_name)))
        ts_files.sort(key=extract_number)

        with open(file_list_path, 'w') as f:
            for ts_file in ts_files:
                relative_path = os.path.relpath(os.path.join(self.temp_folder, ts_file), current_dir)
                f.write(f"file '{relative_path}'\n")

        console.log("[cyan]Start join all file")
        try:
            ffmpeg.input(file_list_path, format='concat', safe=0).output(output_filename, c='copy', loglevel='quiet').run()
        except ffmpeg.Error as e:
            console.log(f"[red]Error saving MP4: {e.stdout}")
            sys.exit(0)
            
        console.log(f"[cyan]Clean ...")
        os.remove(file_list_path)
        shutil.rmtree("tmp", ignore_errors=True)

class M3U8Downloader:
    def __init__(self, m3u8_url, m3u8_audio = None, key=None, output_filename="output.mp4"):
        self.m3u8_url = m3u8_url
        self.m3u8_audio = m3u8_audio
        self.key = key
        self.video_path = output_filename
        self.audio_path = os.path.join("videos", "audio.mp4")

    def start(self):
        video_m3u8 = M3U8(self.m3u8_url, self.key)
        console.log("[green]Download video ts")
        video_m3u8.get_info()
        video_m3u8.download_ts()
        video_m3u8.join(self.video_path)
        print_duration_table(self.video_path)
        print("\n")

        if self.m3u8_audio != None:
            audio_m3u8 = M3U8(self.m3u8_audio, self.key)
            console.log("[green]Download audio ts")
            audio_m3u8.get_info()
            audio_m3u8.download_ts()
            audio_m3u8.join(self.audio_path)
            print_duration_table(self.audio_path)

            self.join_audio()

    def join_audio(self):
        command = [
            "ffmpeg",
            "-y",
            "-i", self.video_path,
            "-i", self.audio_path,
            "-c", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-strict", "experimental",
            self.video_path + ".mp4"
        ]

        try:
            out = subprocess.run(command, check=True, stderr=subprocess.PIPE)
            console.print("\n[green]Merge completed successfully.")
        except subprocess.CalledProcessError as e:
            print("ffmpeg output:", e.stderr.decode())

        os.remove(self.video_path)
        os.remove(self.audio_path)

# [ main function ]
def dw_m3u8(url, audio_url=None, key=None, output_filename="output.mp4"):
    print("\n")
    M3U8Downloader(url, audio_url, key, output_filename).start()
