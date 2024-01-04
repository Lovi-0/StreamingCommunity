# 4.08.2023 -> 14.09.2023 -> 17.09.2023 -> 3.12.2023

# Import
import re, os, sys, glob, time, requests, shutil, ffmpeg, subprocess
from functools import partial
from multiprocessing.dummy import Pool
from tqdm.rich import tqdm
import moviepy.editor as mp

# Class import
from Stream.util.console import console

# Disable warning
import warnings
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


# Variable
main_out_folder = "videos"
os.makedirs(main_out_folder, exist_ok=True)
path_out_without_key = "temp_ts"
path_out_with_key = "out_ts"


# [ decoder ]
def decode_aes_128(path_video_frame, decript_key, x_key):
    frame_name = path_video_frame.split("\\")[-1].split("-")[0] + ".ts"
    iv = x_key["IV"].lstrip("0x") if "IV" in x_key.keys() else ""

    out = subprocess.run([
        "openssl",
        "aes-128-cbc", "-d",
        "-in", path_video_frame,
        "-out", os.path.join(path_out_with_key, frame_name),
        "-nosalt","-iv", iv,
        "-K", decript_key 
    ], capture_output=True)

def decode_ext_x_key(key_str: str):
    key_str = key_str.replace('"', '').lstrip("#EXT-X-KEY:")
    v_list = re.findall(r"[^,=]+", key_str)
    key_map = {v_list[i]: v_list[i+1] for i in range(0, len(v_list), 2)}
    return key_map


# [ util ] 
def save_in_part(folder_ts, merged_mp4, file_extension = ".ts"):

    # Get list of ts file in order
    os.chdir(folder_ts)

    # Order all ts file
    try: ordered_ts_names = sorted(glob.glob(f"*{file_extension}"), key=lambda x:float(re.findall("(\d+)", x.split("_")[1])[0]))
    except: 
        try: ordered_ts_names = sorted(glob.glob(f"*{file_extension}"), key=lambda x:float(re.findall("(\d+)", x.split("-")[1])[0]))
        except: ordered_ts_names = sorted(glob.glob(f"*{file_extension}"))

    open("concat.txt", "wb")
    open("part_list.txt", "wb")

    # Variable for download
    list_mp4_part = []
    part = 0
    start = 0
    end = 200

    # Create mp4 from start ts to end
    def save_part_ts(start, end, part):
        list_mp4_part.append(f"{part}.mp4")

        with open(f"{part}_concat.txt", "w") as f:
            for i in range(start, end):
                f.write(f"file {ordered_ts_names[i]} \n")

        ffmpeg.input(f"{part}_concat.txt", format='concat', safe=0).output(f"{part}.mp4", c='copy', loglevel="quiet").run()


    # Save first part
    save_part_ts(start, end, part)

    # Save all other part
    for _ in range(start, end):

        # Increment progress ts file
        start+= 200
        end += 200
        part+=1

        # Check if end or not
        if(end < len(ordered_ts_names)): 
            save_part_ts(start, end, part)
        else:
            save_part_ts(start, len(ordered_ts_names), part)
            break

    # Merge all part
    console.log(f"[purple]Merge all: {file_extension} file")
    with open("part_list.txt", 'w') as f:
        for mp4_fname in list_mp4_part:
            f.write(f"file {mp4_fname}\n")
            
    ffmpeg.input("part_list.txt", format='concat', safe=0).output(merged_mp4, c='copy', loglevel="quiet").run()
    
def download_ts_file(ts_url: str, store_dir: str, headers):

    # Get ts name and folder
    ts_name = ts_url.split('/')[-1].split("?")[0]
    ts_dir = os.path.join(store_dir, ts_name)

    if(not os.path.isfile(ts_dir)):
        ts_res = requests.get(ts_url, headers=headers)

        if(ts_res.status_code == 200):
            with open(ts_dir, 'wb+') as f:
                f.write(ts_res.content)
        else:
            print(f"Failed to download streaming file: {ts_name}.") 

        time.sleep(0.5)


# [ donwload ]
def dw_m3u8(m3u8_link, m3u8_content, m3u8_headers="", decrypt_key="", merged_mp4="test.mp4"):

    # Reading the m3u8 file
    m3u8_base_url = m3u8_link.rstrip(m3u8_link.split("/")[-1])
    m3u8 = m3u8_content.split('\n')

    ts_url_list = []
    ts_names = []
    x_key_dict = dict()

    is_encryped = False
    os.makedirs(path_out_without_key, exist_ok=True)
    os.makedirs(path_out_with_key, exist_ok=True)

    # Parsing the content in m3u8 with creation of url_list with url of ts file
    for i in range(len(m3u8)):
        if "AES-128" in str(m3u8[i]):
            is_encryped = True

        if m3u8[i].startswith("#EXT-X-KEY:"):
            x_key_dict = decode_ext_x_key(m3u8[i])

        if m3u8[i].startswith("#EXTINF"):
            ts_url = m3u8[i+1]
            ts_names.append(ts_url.split('/')[-1])

            if not ts_url.startswith("http"):
                ts_url = m3u8_base_url + ts_url

            ts_url_list.append(ts_url)
    console.log(f"[blue]Find [white]=> [red]{len(ts_url_list)}[blue] ts file to download")

    if is_encryped and decrypt_key == "": 
        console.log(f"[red]M3U8 Is encryped")
        sys.exit(0)


    #  Using multithreading to download all ts file
    pool = Pool(15)
    gen = pool.imap(partial(download_ts_file, store_dir=path_out_without_key, headers=m3u8_headers), ts_url_list)
    for _ in tqdm(gen, total=len(ts_url_list), unit="bytes", unit_scale=True, unit_divisor=1024, desc="[yellow]Download m3u8"):
        pass
    pool.close()
    pool.join()

    # Merge all ts 
    if is_encryped:
        for ts_fname in tqdm(glob.glob(f"{path_out_without_key}/*.ts"), desc="[yellow]Decoding m3u8"):
            decode_aes_128(ts_fname, decrypt_key, x_key_dict)
        save_in_part(path_out_with_key, merged_mp4)
    else:
        save_in_part(path_out_without_key, merged_mp4)

    # Clean temp file
    os.chdir("..")
    console.log("[green]Clean")

    # Move mp4 file to main folder
    if is_encryped: shutil.move(path_out_with_key+"/"+merged_mp4 , main_out_folder+"/")
    else: shutil.move(path_out_without_key+"/"+merged_mp4 , main_out_folder+"/")

    # Remove folder out_ts and temp_ts
    shutil.rmtree(path_out_with_key, ignore_errors=True)
    shutil.rmtree(path_out_without_key, ignore_errors=True)

def join_audio_to_video(audio_path, video_path, out_path):

    # Get audio and video
    audio = mp.AudioFileClip(audio_path)
    video1 = mp.VideoFileClip(video_path)

    # Add audio
    final = video1.set_audio(audio)

    # Join all
    final.write_videofile(out_path)

