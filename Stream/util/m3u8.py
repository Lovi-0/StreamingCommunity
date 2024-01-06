# 5.01.24

# Import
import requests, re,  os, ffmpeg, shutil
from tqdm.rich import tqdm
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import moviepy.editor as mp

# Class import
from Stream.util.console import console
from Stream.util.headers import get_headers
from Stream.util.util import there_is_audio, merge_ts_files

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
        self.key = bytes.fromhex(key)

        self.temp_folder = "tmp"
        os.makedirs(self.temp_folder, exist_ok=True)
        self.download_audio = False

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
                if self.m3u8_audio != None: self.segments_audio.append(m3u8_audio_line[i+1])

        console.log(f"[cyan]Find: {len(self.segments)} ts file to download")

    def download_m3u8(self):
        response = requests.get(self.m3u8_url, headers={'user-agent': get_headers()})

        if response.ok:
            m3u8_content = response.text
            self.parse_m3u8(m3u8_content)

        # Check there is audio in first ts file
        path_test_ts_file = os.path.join(self.temp_folder, "ts_test.ts")
        if self.key and self.iv:
            open(path_test_ts_file, "wb").write(self.decrypt_ts(requests.get(self.segments[0]).content))
        else:
            open(path_test_ts_file, "wb").write(requests.get(self.segments[0]).content)

        if not there_is_audio(path_test_ts_file):
            self.download_audio = True
            console.log("[cyan]=> Make req to get video and audio file")

        os.remove(path_test_ts_file)

    def decrypt_ts(self, encrypted_data):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data
    
    def decrypt_and_save(self, index):
        
        video_ts_url = self.segments[index]
        video_ts_filename = os.path.join(self.temp_folder, f"{index}_v.ts")

        if self.download_audio: 
            audio_ts_url = self.segments_audio[index]
            audio_ts_filename = os.path.join(self.temp_folder, f"{index}_a.ts")
            video_audio_ts_filename = os.path.join(self.temp_folder, f"{index}_v_a.ts")

        # Download video or audio ts file 
        if not os.path.exists(video_ts_url):
            ts_response = requests.get(video_ts_url, headers={'user-agent': get_headers()}).content

            if self.key and self.iv:
                decrypted_data = self.decrypt_ts(ts_response)
                with open(video_ts_filename, "wb") as ts_file:
                    ts_file.write(decrypted_data)

            else:
                with open(video_ts_filename, "wb") as ts_file:
                    ts_file.write(ts_response)

        # Donwload only audio ts file
        if self.download_audio:
            ts_response = requests.get(audio_ts_url, headers={'user-agent': get_headers()}).content

            if self.key and self.iv:
                decrypted_data = self.decrypt_ts(ts_response)
                with open(audio_ts_filename, "wb") as ts_file:
                    ts_file.write(decrypted_data)

            else:
                with open(audio_ts_filename, "wb") as ts_file:
                    ts_file.write(ts_response)
            
            # Join ts video and audio
            merge_ts_files(video_ts_filename, audio_ts_filename, video_audio_ts_filename)
            os.remove(video_ts_filename)
            os.remove(audio_ts_filename)
        
    def download_and_save_ts(self):
        with ThreadPoolExecutor(max_workers=30) as executor:
            list(tqdm(executor.map(self.decrypt_and_save, range(len(self.segments)) ), total=len(self.segments), unit="bytes", unit_scale=True, unit_divisor=1024, desc="[yellow]Download"))
            
    def join_ts_files(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_list_path = os.path.join(current_dir, 'file_list.txt')

        ts_files = [f for f in os.listdir(self.temp_folder) if f.endswith(".ts")]
        ts_files.sort()

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
            print(f"Errore durante il salvataggio del file MP4: {e}")
        finally:
            os.remove(file_list_path)
            shutil.rmtree("tmp", ignore_errors=True)


# [ function ]
def dw_m3u8(url, audio_url=None, key=None, output_filename="output.mp4"):

    downloader = M3U8Downloader(url, audio_url, key, output_filename)

    downloader.download_m3u8()
    downloader.download_and_save_ts()
    downloader.join_ts_files()

def join_audio_to_video(audio_path, video_path, out_path):

    # Get audio and video
    audio = mp.AudioFileClip(audio_path)
    video1 = mp.VideoFileClip(video_path)

    # Add audio
    final = video1.set_audio(audio)

    # Join all
    final.write_videofile(out_path)
