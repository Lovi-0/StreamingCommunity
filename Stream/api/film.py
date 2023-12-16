# 3.12.23 -> 10.12.23

# Class import
from Stream.util.headers import get_headers
from Stream.util.console import console
from Stream.util.m3u8 import dw_m3u8

# General import
import requests, sys, re, json
from bs4 import BeautifulSoup

# [func]
def get_iframe(id_title, domain):
    req_iframe = requests.get(url = f"https://streamingcommunity.{domain}/iframe/{id_title}", headers = {
        "User-agent": get_headers()
    })

    url_embed = BeautifulSoup(req_iframe.text, "lxml").find("iframe").get("src")
    req_embed = requests.get(url_embed, headers = {"User-agent": get_headers()}).text
    return BeautifulSoup(req_embed, "lxml").find("body").find("script").text
    
def parse_content(embed_content):

    # Parse parameter from req embed content
    win_video = re.search(r"window.video = {.*}", str(embed_content)).group()
    win_param = re.search(r"params: {[\s\S]*}", str(embed_content)).group()

    # Parse parameter to make read for json
    json_win_video = "{"+win_video.split("{")[1].split("}")[0]+"}"
    json_win_param = "{"+win_param.split("{")[1].split("}")[0].replace("\n", "").replace(" ", "") + "}"
    json_win_param = json_win_param.replace(",}", "}").replace("'", '"')
    return json.loads(json_win_video), json.loads(json_win_param)

def get_m3u8_url(json_win_video, json_win_param):
    return f"https://vixcloud.co/playlist/{json_win_video['id']}?type=video&rendition=720p&token={json_win_param['token720p']}&expires={json_win_param['expires']}"

def get_m3u8_key(json_win_video, json_win_param, title_name):
    req_key = requests.get('https://vixcloud.co/storage/enc.key', headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param["token720p"]}&title={title_name.replace(" ", "+")}&referer=1&expires={json_win_param["expires"]}',
    }).content

    return "".join(["{:02x}".format(c) for c in req_key])

def main_dw_film(id_film, title_name, domain):

    embed_content = get_iframe(id_film, domain)
    json_win_video, json_win_param = parse_content(embed_content)
    m3u8_url = get_m3u8_url(json_win_video, json_win_param)
    m3u8_key = get_m3u8_key(json_win_video, json_win_param, title_name)
    
    dw_m3u8(m3u8_url, requests.get(m3u8_url, headers={"User-agent": get_headers()}).text, "", m3u8_key, str(title_name).replace("+", " ").replace(",", "") + ".mp4")
