# 3.12.23 -> 10.12.23

# Class import
from Src.Util.headers import get_headers
from Src.Util.console import console, msg
from Src.Util.config import config
from Src.Lib.FFmpeg.my_m3u8 import download_m3u8

# General import
import requests, os, re, json, sys, binascii, urllib
from bs4 import BeautifulSoup


# [func]
def get_token(id_tv, domain):
    session = requests.Session()
    session.get(f"https://streamingcommunity.{domain}/watch/{id_tv}")
    return session.cookies['XSRF-TOKEN']


def get_info_tv(id_film, title_name, site_version, domain):

    req = requests.get(f"https://streamingcommunity.{domain}/titles/{id_film}-{title_name}", headers={
        'X-Inertia': 'true', 
        'X-Inertia-Version': site_version,
        'User-Agent': get_headers()
    })

    if req.ok:
        return req.json()['props']['title']['seasons_count']
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)


def get_info_season(tv_id, tv_name, domain, version, token, n_stagione):
    req = requests.get(f'https://streamingcommunity.{domain}/titles/{tv_id}-{tv_name}/stagione-{n_stagione}', headers={
        'authority': f'streamingcommunity.{domain}', 'referer': f'https://streamingcommunity.broker/titles/{tv_id}-{tv_name}',
        'user-agent': get_headers(), 'x-inertia': 'true', 'x-inertia-version': version, 'x-xsrf-token': token,
    })

    if req.ok:
        return [{'id': ep['id'], 'n': ep['number'], 'name': ep['name']} for ep in req.json()['props']['loadedSeason']['episodes']]
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)


def get_iframe(tv_id, ep_id, domain, token):
    req = requests.get(f'https://streamingcommunity.{domain}/iframe/{tv_id}', params={'episode_id': ep_id, 'next_episode': '1'}, cookies={'XSRF-TOKEN': token}, headers={
        'referer': f'https://streamingcommunity.{domain}/watch/{tv_id}?e={ep_id}',
        'user-agent': get_headers()
    })

    # Change user agent m3u8
    custom_headers_req = {
        'referer': f'https://streamingcommunity.{domain}/watch/{tv_id}?e={ep_id}',
        'user-agent': get_headers()
    }

    if req.ok:
        url_embed = BeautifulSoup(req.text, "lxml").find("iframe").get("src")
        req_embed = requests.get(url_embed, headers = {"User-agent": get_headers()}).text
        return BeautifulSoup(req_embed, "lxml").find("body").find("script").text
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


def get_playlist(json_win_video, json_win_param, render_quality):
    token_render = f"token{render_quality}"
    return f"https://vixcloud.co/playlist/{json_win_video['id']}?token={json_win_param['token']}&{token_render}={json_win_param[token_render]}&expires={json_win_param['expires']}"


def get_m3u8_url(json_win_video, json_win_param, render_quality):
    token_render = f"token{render_quality}"
    return f"https://vixcloud.co/playlist/{json_win_video['id']}?type=video&rendition={render_quality}&token={json_win_param[token_render]}&expires={json_win_param['expires']}"


def get_m3u8_key_ep(json_win_video, json_win_param, tv_name, n_stagione, n_ep, ep_title, token_render):
    response = requests.get('https://vixcloud.co/storage/enc.key', headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param[token_render]}&title={tv_name}&referer=1&expires={json_win_param["expires"]}&description=S{n_stagione}%3AE{n_ep}+{ep_title}&nextEpisode=1',
    })

    if response.ok:
        return binascii.hexlify(response.content).decode('utf-8')
    else:
        console.log(f"[red]Error: {response.status_code}")
        sys.exit(0)

def get_m3u8_playlist(json_win_video, json_win_param, tv_name, n_stagione, n_ep, ep_title, token_render):
    req = requests.get(f'https://vixcloud.co/playlist/{json_win_video["id"]}', params={'token': json_win_param['token'], 'expires': json_win_param["expires"] }, headers={
        'referer': f'https://vixcloud.co/embed/{json_win_video["id"]}?token={json_win_param[token_render]}&title={tv_name}&referer=1&expires={json_win_param["expires"]}&description=S{n_stagione}%3AE{n_ep}+{ep_title}&nextEpisode=1'
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
def dw_single_ep(tv_id, eps, index_ep_select, domain, token, tv_name, season_select):

    encoded_name = urllib.parse.quote(eps[index_ep_select]['name'])

    console.print(f"[green]Downloading episode: [blue]{eps[index_ep_select]['n']} [green]=> [purple]{eps[index_ep_select]['name']}")
    embed_content = get_iframe(tv_id, eps[index_ep_select]['id'], domain, token)
    json_win_video, json_win_param, render_quality = parse_content(embed_content)

    token_render = f"token{render_quality}"
    console.print(f"[blue]Selected quality => [red]{render_quality}")

    m3u8_playlist = get_playlist(json_win_video, json_win_param, render_quality)
    m3u8_url = get_m3u8_url(json_win_video, json_win_param, render_quality)
    m3u8_key = get_m3u8_key_ep(json_win_video, json_win_param, tv_name, season_select, index_ep_select+1, encoded_name, token_render)

    mp4_name = f"{tv_name.replace('+', '_')}_S{str(season_select).zfill(2)}E{str(index_ep_select+1).zfill(2)}"
    mp4_format = f"{mp4_name}.mp4"
    season = mp4_name.rsplit("E", 1)[0]
    mp4_path = os.path.join(config['root_path'], config['series_folder_name'], tv_name, season, mp4_format)

    m3u8_url_audio = get_m3u8_playlist(json_win_video, json_win_param, tv_name, season_select, index_ep_select+1, encoded_name, token_render)

    if m3u8_url_audio is not None:
        console.print("[blue]Using m3u8 audio => [red]True")
    # Movie_Name.[Language_Code].vtt
    # Movie_Name.[Language_Code].forced.vtt
    subtitle_path = os.path.join(config['root_path'], config['series_folder_name'], mp4_name, season)
    download_m3u8(m3u8_index=m3u8_url, m3u8_audio=m3u8_url_audio, m3u8_subtitle=m3u8_playlist, key=m3u8_key, output_filename=mp4_path, subtitle_folder=subtitle_path, content_name=mp4_name)


def main_dw_tv(tv_id, tv_name, version, domain):

    token = get_token(tv_id, domain)

    num_season_find = get_info_tv(tv_id, tv_name, version, domain)
    console.print("\n[green]Insert season [red]number[green], or [red](*) [green]to download all seasons, or [red][1-2] [green]for a range of seasons")
    console.print(f"\n[blue]Season(s) found: [red]{num_season_find}")
    season_select = str(msg.ask("\n[green]Insert which season(s) number you'd like to download"))
    if "[" in season_select:
        start, end = map(int, season_select[1:-1].split('-'))
        result = list(range(start, end + 1))
        for n_season in result:
            eps = get_info_season(tv_id, tv_name, domain, version, token, n_season)
            for ep in eps:
                dw_single_ep(tv_id, eps, int(ep['n'])-1, domain, token, tv_name, n_season)
                print("\n")
    elif season_select != "*":
        season_select = int(season_select)
        if 1 <= season_select <= num_season_find:
            eps = get_info_season(tv_id, tv_name, domain, version, token, season_select)

            for ep in eps:
                console.print(f"[green]Episode: [blue]{ep['n']} [green]=> [purple]{ep['name']}")
            index_ep_select = str(msg.ask("\n[green]Insert episode [blue]number[green], or [red](*) [green]to download all episodes, or [red][1-2] [green]for a range of episodes"))

            # Download range []
            if "[" in index_ep_select:
                start, end = map(int, index_ep_select[1:-1].split('-'))
                result = list(range(start, end + 1))

                for n_randge_ep in result:
                    index_ep_select = int(n_randge_ep)
                    dw_single_ep(tv_id, eps, n_randge_ep-1, domain, token, tv_name, season_select)

            # Download single ep
            elif index_ep_select != "*":
                if 1 <= int(index_ep_select) <= len(eps):
                    index_ep_select = int(index_ep_select) - 1
                    dw_single_ep(tv_id, eps, index_ep_select, domain, token, tv_name, season_select)
                else:
                    console.print("[red]Wrong [yellow]INDEX [red]for the selected Episode")

            # Download all
            else:
                for ep in eps:
                    dw_single_ep(tv_id, eps, int(ep['n'])-1, domain, token, tv_name, season_select)
                    print("\n")

        else:
            console.print("[red]Wrong [yellow]INDEX for the selected Season")
    else:
        for n_season in range(1, num_season_find+1):
            eps = get_info_season(tv_id, tv_name, domain, version, token, n_season)
            for ep in eps:
                dw_single_ep(tv_id, eps, int(ep['n'])-1, domain, token, tv_name, n_season)
                print("\n")
            
