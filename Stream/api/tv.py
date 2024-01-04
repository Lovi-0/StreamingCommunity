# 3.12.23 -> 10.12.23

# Class import
from Stream.util.headers import get_headers
from Stream.util.console import console, msg, console_print
from Stream.util.m3u8 import dw_m3u8, join_audio_to_video

# General import
import requests, os, re, json
from bs4 import BeautifulSoup

# [func]
def get_token(id_tv, domain):
    session = requests.Session()
    session.get(f"https://streamingcommunity.{domain}/watch/{id_tv}")
    return session.cookies['XSRF-TOKEN']

def get_info_tv(id_film, title_name, site_version, domain):
    r = requests.get(f"https://streamingcommunity.{domain}/titles/{id_film}-{title_name}", headers={
        'X-Inertia': 'true', 
        'X-Inertia-Version': site_version,
        'User-Agent': get_headers()
    })

    return r.json()['props']['title']['seasons_count']

def get_info_season(tv_id, tv_name, domain, version, token, n_stagione):
    r = requests.get(f'https://streamingcommunity.{domain}/titles/{tv_id}-{tv_name}/stagione-{n_stagione}', headers={
        'authority': f'streamingcommunity.{domain}', 'referer': f'https://streamingcommunity.broker/titles/{tv_id}-{tv_name}',
        'user-agent': get_headers(), 'x-inertia': 'true', 'x-inertia-version': version, 'x-xsrf-token': token,
    })

    return [{'id': ep['id'], 'n': ep['number'], 'name': ep['name']} for ep in r.json()['props']['loadedSeason']['episodes']]

def get_iframe(tv_id, ep_id, domain, token):
    r = requests.get(f'https://streamingcommunity.{domain}/iframe/{tv_id}', params={'episode_id': ep_id, 'next_episode': '1'}, cookies={'XSRF-TOKEN': token}, headers={
        'referer': f'https://streamingcommunity.{domain}/watch/{tv_id}?e={ep_id}',
        'user-agent': get_headers()
    })

    url_embed = BeautifulSoup(r.text, "lxml").find("iframe").get("src")
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

def get_m3u8_key_ep(json_win_video, json_win_param, tv_name, n_stagione, n_ep, ep_title):
    req_key = requests.get('https://vixcloud.co/storage/enc.key', headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param["token720p"]}&title={tv_name.replace("-", "+")}&referer=1&expires={json_win_param["expires"]}&description=S{n_stagione}%3AE{n_ep}+{ep_title.replace(" ", "+")}&nextEpisode=1',
    }).content

    return "".join(["{:02x}".format(c) for c in req_key])

def get_m3u8_audio(json_win_video, json_win_param, tv_name, n_stagione, n_ep, ep_title):

    response = requests.get(f'https://vixcloud.co/playlist/{json_win_video["id"]}', params={'token': json_win_param['token'], 'expires': json_win_param["expires"] }, headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param["token720p"]}&title={tv_name.replace("-", "+")}&referer=1&expires={json_win_param["expires"]}&description=S{n_stagione}%3AE{n_ep}+{ep_title.replace(" ", "+")}&nextEpisode=1'
    })

    m3u8_cont = response.text.split()
    for row in m3u8_cont:
        if "audio" in str(row) and "ita" in str(row):
            return row.split(",")[-1].split('"')[-2]

 
def main_dw_tv(tv_id, tv_name, version, domain):

    token = get_token(tv_id, domain)

    tv_name = str(tv_name.replace('+', '-')).lower()
    console.log(f"[blue]Season find: [red]{get_info_tv(tv_id, tv_name, version, domain)}")
    season_select = msg.ask("[green]Insert season number: ")

    eps = get_info_season(tv_id, tv_name, domain, version, token, season_select)
    for ep in eps:
        console_print(f"[green]Ep: [blue]{ep['n']} [green]=> [purple]{ep['name']}")
    index_ep_select = int(msg.ask("[green]Insert ep number: ")) - 1
    
    embed_content = get_iframe(tv_id, eps[index_ep_select]['id'], domain, token)
    json_win_video, json_win_param = parse_content(embed_content)
    m3u8_url = get_m3u8_url(json_win_video, json_win_param)
    m3u8_key = get_m3u8_key_ep(json_win_video, json_win_param, tv_name, season_select, index_ep_select+1, eps[index_ep_select]['name'])

    dw_m3u8(m3u8_url, requests.get(m3u8_url, headers={"User-agent": get_headers()}).text, "", m3u8_key, tv_name.replace("+", "_") + "_"+str(season_select)+"__"+str(index_ep_select+1) + ".mp4")

    is_down_audio = msg.ask("[blue]Download audio [red](!!! Only for recent upload, !!! Use all CPU) [blue][y \ n]").strip()
    if str(is_down_audio) == "y": 
        m3u8_url_audio = get_m3u8_audio(json_win_video, json_win_param, tv_name, season_select, index_ep_select+1, eps[index_ep_select]['name'])
        dw_m3u8(m3u8_url_audio, requests.get(m3u8_url_audio, headers={"User-agent": get_headers()}).text, "", m3u8_key, "audio.mp4")

        join_audio_to_video("videos//audio.mp4", "videos//" + tv_name.replace("+", "_") + "_"+str(season_select)+"__"+str(index_ep_select+1) + ".mp4", "videos//" + tv_name.replace("+", "_") + "_"+str(season_select)+"__"+str(index_ep_select+1) + "_audio.mp4")
        os.remove("videos//audio.mp4")
        os.remove("videos//" + tv_name.replace("+", "_") + "_"+str(season_select)+"__"+str(index_ep_select+1) + ".mp4")