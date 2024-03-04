# 3.12.23 -> 10.12.23

# Class import
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util.config import config
from Src.Lib.FFmpeg.my_m3u8 import download_m3u8

# General import
import requests, os, re, json, sys, binascii
from bs4 import BeautifulSoup

# [func]
def get_iframe(id_title, domain):
    req = requests.get(url = f"https://streamingcommunity.{domain}/iframe/{id_title}", headers = {
        "User-agent": get_headers()
    })

    if req.ok:
        url_embed = BeautifulSoup(req.text, "lxml").find("iframe").get("src")
        req_embed = requests.get(url_embed, headers = {"User-agent": get_headers()}).text

        try:
            return BeautifulSoup(req_embed, "lxml").find("body").find("script").text
        except:
            console.log("[red]Couldn't play this video file (video not available)")
            sys.exit(0)

    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)
    
def select_quality(json_win_param):

    if json_win_param['token1080p']:
        return "1080p"
    elif json_win_param['token720p']:
        return "720p"
    elif json_win_param['token480p']:
        return "480p"
    else:
        return "360p"

def parse_content(embed_content):

    # Parse parameter from req embed content
    win_video = re.search(r"window.video = {.*}", str(embed_content)).group()
    win_param = re.search(r"params: {[\s\S]*}", str(embed_content)).group()

    # Parse parameter to make read for json
    json_win_video = "{"+win_video.split("{")[1].split("}")[0]+"}"
    json_win_param = "{"+win_param.split("{")[1].split("}")[0].replace("\n", "").replace(" ", "") + "}"
    json_win_param = json_win_param.replace(",}", "}").replace("'", '"')
    return json.loads(json_win_video), json.loads(json_win_param), select_quality(json.loads(json_win_param))

def get_m3u8_url(json_win_video, json_win_param, render_quality):
    token_render = f"token{render_quality}"
    return f"https://vixcloud.co/playlist/{json_win_video['id']}?type=video&rendition={render_quality}&token={json_win_param[token_render]}&expires={json_win_param['expires']}"

def get_m3u8_key(json_win_video, json_win_param, title_name, token_render):
    response = requests.get('https://vixcloud.co/storage/enc.key', headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param[token_render]}&title={title_name}&referer=1&expires={json_win_param["expires"]}',
    })

    if response.ok:
        return binascii.hexlify(response.content).decode('utf-8')
    else:
        console.log(f"[red]Error: {response.status_code}")
        sys.exit(0)

def get_m3u8_audio(json_win_video, json_win_param, title_name, token_render):
    req = requests.get(f'https://vixcloud.co/playlist/{json_win_video["id"]}', params={'token': json_win_param['token'], 'expires': json_win_param["expires"] }, headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param[token_render]}&title={title_name}&referer=1&expires={json_win_param["expires"]}'
    })

    if req.ok:
        m3u8_cont = req.text.split()
        for row in m3u8_cont:
            if "audio" in str(row) and "ita" in str(row):
                return row.split(",")[-1].split('"')[-2]
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)
        

# [func \ main]
def main_dw_film(id_film, title_name, domain):

    embed_content = get_iframe(id_film, domain)
    json_win_video, json_win_param, render_quality = parse_content(embed_content)

    token_render = f"token{render_quality}"
    console.print(f"[blue]Selected quality => [red]{render_quality}")

    m3u8_url = get_m3u8_url(json_win_video, json_win_param, render_quality)
    m3u8_key = get_m3u8_key(json_win_video, json_win_param, title_name, token_render)

    mp4_name = title_name.replace("+", " ").replace(",", "").replace("-", "_")
    mp4_format = mp4_name + ".mp4"
    mp4_path = os.path.join(config['root_path'], config['film_folder_name'], mp4_name, mp4_format)

    m3u8_url_audio = get_m3u8_audio(json_win_video, json_win_param, title_name, token_render)

    if m3u8_url_audio != None:
        console.print("[blue]Using m3u8 audio => [red]True")
        
    download_m3u8(m3u8_index=m3u8_url, m3u8_audio=m3u8_url_audio, m3u8_subtitle=m3u8_url, key=m3u8_key, output_filename=mp4_path)
