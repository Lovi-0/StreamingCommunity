# 5.01.24 -> 7.01.24

# Import
import requests, re,  os, ffmpeg, shutil, time, sys, warnings
from tqdm.rich import tqdm
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Class import
from Src.Util.Helper.console import console
from Src.Util.Helper.headers import get_headers
from Src.Util.Helper.util import there_is_audio, merge_ts_files


# Disable warning
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="cryptography")


# Variable
os.makedirs("videos", exist_ok=True)


# [ main class ]
class M3U8Downloader:

    def __init__(self, m3u8_url, m3u8_audio = None, key=None, output_filename="output.mp4"):
        self.m3u8_url = m3u8_url
        self.m3u8_audio = m3u8_audio
        self.key = key
        self.output_filename = output_filename
        
        self.segments = []
        self.segments_audio = []
        self.iv = None
        if key != None: self.key = bytes.fromhex(key)

        self.temp_folder = "tmp"
        os.makedirs(self.temp_folder, exist_ok=True)
        self.download_audio = False
        self.max_retry = 3
        self.failed_segments = []

    def decode_ext_x_key(self, key_str):
        key_str = key_str.replace('"', '').lstrip("#EXT-X-KEY:")
        v_list = re.findall(r"[^,=]+", key_str)
        key_map = {v_list[i]: v_list[i+1] for i in range(0, len(v_list), 2)}

        return key_map # URI | METHOD | IV

    def parse_key(self, raw_iv):
        self.iv = bytes.fromhex(raw_iv.replace("0x", ""))

    def parse_m3u8(self, m3u8_content):
        if self.m3u8_audio != None: 
            m3u8_audio_line = str(requests.get(self.m3u8_audio).content).split("\\n")

        m3u8_base_url = self.m3u8_url.rstrip(self.m3u8_url.split("/")[-1])
        lines = m3u8_content.split('\n')

        for i in range(len(lines)):
            line = str(lines[i])

            if line.startswith("#EXT-X-KEY:"):
                x_key_dict = self.decode_ext_x_key(line)
                self.parse_key(x_key_dict['IV'])

            if line.startswith("#EXTINF"):
                ts_url = lines[i+1]

                if not ts_url.startswith("http"):
                    ts_url = m3u8_base_url + ts_url

                self.segments.append(ts_url)

                if self.m3u8_audio != None: 
                    self.segments_audio.append(m3u8_audio_line[i+1])

        console.log(f"[cyan]Find: {len(self.segments)} ts file to download")

        # Check video ts segment
        if len(self.segments) == 0:
            console.log("[red]No ts files to download")
            sys.exit(0)

        # Check audio ts segment
        if self.m3u8_audio != None:
            console.log(f"[cyan]Find: {len(self.segments_audio)} ts audio file to download")

            if len(self.segments_audio) == 0:
                console.log("[red]No ts audio files to download")
                sys.exit(0)

    def download_m3u8(self):
        response = requests.get(self.m3u8_url, headers={'user-agent': get_headers()})

        if response.ok:
            m3u8_content = response.text
            self.parse_m3u8(m3u8_content)
        else:
            console.log("[red]Wrong m3u8 url")
            sys.exit(0)

        if self.m3u8_audio != None:

            # Check there is audio in first ts file
            path_test_ts_file = os.path.join(self.temp_folder, "ts_test.ts")
            if self.key and self.iv:
                open(path_test_ts_file, "wb").write(self.decrypt_ts(requests.get(self.segments[0]).content))
            else:
                open(path_test_ts_file, "wb").write(requests.get(self.segments[0]).content)

            if not there_is_audio(path_test_ts_file):
                self.download_audio = True
                #console.log("[yellow]=> Make req to get video and audio file")

            #console.log("[yellow]=> Download audio")
            os.remove(path_test_ts_file)

    def decrypt_ts(self, encrypted_data):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data
    
    def make_req_single_ts_file(self, ts_url, retry=0):

        if retry == self.max_retry:
            console.log(f"[red]Failed download: {ts_url}")
            self.segments.remove(ts_url)
            return None

        req = requests.get(ts_url, headers={'user-agent': get_headers()}, timeout=10, allow_redirects=True)

        if req.status_code == 200:
            return req.content
        else:
            retry += 1
            return self.make_req_single_ts_file(ts_url, retry)

    def decrypt_and_save(self, index):
        
        video_ts_url = self.segments[index]
        video_ts_filename = os.path.join(self.temp_folder, f"{index}_v.ts")

        # Download video or audio ts file 
        if not os.path.exists(video_ts_filename):   # Only for media that not use audio
            ts_response = self.make_req_single_ts_file(video_ts_url)

            if ts_response != None:
                if self.key and self.iv:
                    decrypted_data = self.decrypt_ts(ts_response)
                    with open(video_ts_filename, "wb") as ts_file:
                        ts_file.write(decrypted_data)

                else:
                    with open(video_ts_filename, "wb") as ts_file:
                        ts_file.write(ts_response)

        # Donwload only audio ts file and merge with video
        if self.download_audio: 
            audio_ts_url = self.segments_audio[index]
            audio_ts_filename = os.path.join(self.temp_folder, f"{index}_a.ts")
            video_audio_ts_filename = os.path.join(self.temp_folder, f"{index}_v_a.ts")

            if not os.path.exists(video_audio_ts_filename):  # Only for media use audio
                ts_response = self.make_req_single_ts_file(audio_ts_url)

                if ts_response != None:
                    if self.key and self.iv:
                        decrypted_data = self.decrypt_ts(ts_response)

                        with open(audio_ts_filename, "wb") as ts_file:
                            ts_file.write(decrypted_data)

                    else:
                        with open(audio_ts_filename, "wb") as ts_file:
                            ts_file.write(ts_response)
                    
                    # Join ts video and audio
                    res_merge = merge_ts_files(video_ts_filename, audio_ts_filename, video_audio_ts_filename)

                    if res_merge:
                        os.remove(video_ts_filename)
                        os.remove(audio_ts_filename)

                    # If merge fail, so we have only video and audio, take only video
                    else:
                        self.failed_segments.append(index)
                        os.remove(audio_ts_filename)
                         
    def download_and_save_ts(self):
        with ThreadPoolExecutor(max_workers=30) as executor:
            list(tqdm(executor.map(self.decrypt_and_save, range(len(self.segments)) ), total=len(self.segments), unit="bytes", unit_scale=True, unit_divisor=1024, desc="[yellow]Download"))
        
        if len(self.failed_segments) > 0:
            console.log(f"[red]Segment ts: {self.failed_segments}, cant use audio")

    def join_ts_files(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_list_path = os.path.join(current_dir, 'file_list.txt')

        # Make sort by number
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
            (
                ffmpeg.input(file_list_path, format='concat', safe=0).output(self.output_filename, c='copy', loglevel='quiet').run()
            )
            console.log(f"[cyan]Clean ...")
        except ffmpeg.Error as e:
            console.log(f"[red]Error saving MP4: {e.stdout}")
            sys.exit(0)
        
        time.sleep(2)
        os.remove(file_list_path)
        shutil.rmtree("tmp", ignore_errors=True)


# [ main function ]
def dw_m3u8(url, audio_url=None, key=None, output_filename="output.mp4"):

    downloader = M3U8Downloader(url, audio_url, key, output_filename)

    downloader.download_m3u8()
    downloader.download_and_save_ts()
    downloader.join_ts_files()
