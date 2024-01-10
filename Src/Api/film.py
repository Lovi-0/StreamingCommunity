# 3.12.23 -> 10.12.23

# Class import
from Src.Util.Helper.headers import get_headers
from Src.Util.Helper.util import convert_utf8_name
from Src.Util.Helper.console import console
from Src.Util.m3u8 import dw_m3u8

# General import
import requests, os, re, json, sys
from bs4 import BeautifulSoup

# [func]
def get_iframe(id_title, domain):
    req = requests.get(url = f"https://streamingcommunity.{domain}/iframe/{id_title}", headers = {
        "User-agent": get_headers()
    })

    if req.ok:
        url_embed = BeautifulSoup(req.text, "lxml").find("iframe").get("src")
        req_embed = requests.get(url_embed, headers = {"User-agent": get_headers()}).text
        return BeautifulSoup(req_embed, "lxml").find("body").find("script").text
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)
    
def parse_content(embed_content):

    # Parse parameter from req embed content
    win_video = re.search(r"window.video = {.*}", str(embed_content)).group()
    win_param = re.search(r"params: {[\s\S]*}", str(embed_content)).group()

    # Parse parameter to make read for json
    json_win_video = "{"+win_video.split("{")[1].split("}")[0]+"}"
    json_win_param = "{"+win_param.split("{")[1].split("}")[0].replace("\n", "").replace(" ", "") + "}"
    json_win_param = json_win_param.replace(",}", "}").replace("'", '"')
    return json.loads(json_win_video), json.loads(json_win_param)

def get_m3u8_url(json_win_video, json_win_param, render_quality):
    token_render = f"token{render_quality}"
    return f"https://vixcloud.co/playlist/{json_win_video['id']}?type=video&rendition={render_quality}&token={json_win_param[token_render]}&expires={json_win_param['expires']}"

def get_m3u8_key(json_win_video, json_win_param, title_name, token_render):
    req = requests.get('https://vixcloud.co/storage/enc.key', headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param[token_render]}&title={title_name.replace(" ", "+")}&referer=1&expires={json_win_param["expires"]}',
    })

    if req.ok:
        return "".join(["{:02x}".format(c) for c in req.content])
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)
        
def main_dw_film(id_film, title_name, domain):

    lower_title_name = str(title_name).lower()
    title_name = convert_utf8_name(lower_title_name)   # ERROR LATIN 1 IN REQ WITH ò à ù ...

    embed_content = get_iframe(id_film, domain)
    json_win_video, json_win_param = parse_content(embed_content)

    # Select first availability video quaklity
    if json_win_param['token1080p'] != "": render_quality = "1080p"
    elif json_win_param['token720p'] != "": render_quality = "720p"
    elif json_win_param['token480p'] != "": render_quality = "480p"
    else: render_quality = "360p"
    token_render = f"token{render_quality}"
    console.print(f"[blue]Quality select => [red]{render_quality}")

    m3u8_url = get_m3u8_url(json_win_video, json_win_param, render_quality)
    m3u8_key = get_m3u8_key(json_win_video, json_win_param, title_name, token_render)
    
    path_film = os.path.join("videos", lower_title_name.replace("+", " ").replace(",", "") + ".mp4")
    dw_m3u8(m3u8_url, None, m3u8_key, path_film)
