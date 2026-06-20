import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import unquote


REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}


def get_actor_info(name: str, actor_info_dir: str) -> dict | None:
    info_file = f'{actor_info_dir}/{name}/info.json'
    if not os.path.exists(info_file):
        return None
    with open(info_file, 'r') as f:
        info = json.load(f)
    return info if info else None


def fetch_actor_info(name: str, actor_info_dir: str) -> dict | None:
    return _scrape_actor_info(name, actor_info_dir, download_media=True)


def _scrape_actor_info(name: str, save_dir: str, download_media: bool = True) -> dict | None:
    info = {'name': name, 'date_of_birth': None, 'galleries': [], 'aka': []}

    info_bp = _scrape_babepedia(name, save_dir, download_media=download_media)
    if info_bp is None:
        return None

    if 'Born' in info_bp:
        info['date_of_birth'] = _format_date_of_birth(info_bp['Born'])
    info['aka'] = info_bp.get('aka', [])
    info['babepedia'] = info_bp

    _save_actor_info(save_dir, name, info)

    if download_media and info_bp['galleries']:
        gall_paths = _download_actor_galleries(save_dir, name, info_bp['galleries'])
        info['galleries'] = gall_paths
        _save_actor_info(save_dir, name, info)

    return info


def _scrape_babepedia(name: str, save_dir: str, download_media: bool = True) -> dict | None:
    res = _get_babepedia_page_by_name(name)
    if res.status_code == 504:
        raise Exception("504 Server Error: Gateway timeout")
    res.raise_for_status()

    if '/search/' in res.url:
        return None

    soup = BeautifulSoup(res.content, 'html.parser')
    info = _parse_babepedia_info(soup)
    return {'url': res.url} | info


def _get_babepedia_page_by_name(name: str):
    url = 'https://www.babepedia.com/babe/' + name.replace(' ', '_')
    return requests.get(url, headers=REQUEST_HEADERS)


def _parse_babepedia_info(soup) -> dict:
    info: dict = {'last_scraped': str(datetime.now())[:10]}
    info |= _get_personal_info(soup)

    try:
        info['bio'] = soup.select_one('#biotext').text
    except Exception:
        pass

    try:
        info['aka'] = soup.select_one('#aka').text.replace('Also known as: ', '').replace('\xa0', '').split(' - ')
    except Exception:
        pass

    comments = _get_bp_comments(soup)
    if comments:
        info['comments'] = comments

    galls = []
    for gall in soup.select('.gallery'):
        for a_el in gall.select('a'):
            if '.php?' not in a_el['href']:
                galls.append(a_el['href'])
    info['galleries'] = galls

    return info


def _get_personal_info(soup) -> dict:
    info_items = soup.select('#personal-info-block .info-item:not(.info-title)')
    info = {}
    for info_item in info_items:
        label = info_item.select_one('.label').text
        value = info_item.select_one('.value').text
        info[label.replace(':', '')] = value
    return info


def _format_date_of_birth(born: str) -> str:
    parts = born.split()
    day = ''.join(filter(str.isdigit, parts[1]))
    cleaned = f"{parts[0]} {day} of {parts[3]} {parts[4]}"
    dt = datetime.strptime(cleaned, '%A %d of %B %Y')
    return dt.strftime('%Y-%m-%d')


def _get_bp_comments(soup) -> list | None:
    comment_els = soup.select('.commentbox .comment')
    return [el.text for el in comment_els] if comment_els else None


def _download_actor_galleries(save_dir: str, name: str, galleries: list, redo: bool = False) -> list:
    RELATIVE_BASE = f'{name}/media/babepedia'
    paths = []
    for gall in galleries:
        url = 'https://www.babepedia.com' + gall
        img_path = f'{save_dir}/{RELATIVE_BASE}{unquote(gall)}'
        if redo or not os.path.exists(img_path):
            try:
                _download_image(url, img_path)
            except requests.HTTPError:
                pass
        if os.path.exists(img_path):
            paths.append(img_path.replace(save_dir, ''))
    return paths


def _download_image(url: str, img_path: str) -> str:
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.raise_for_status()
    with open(img_path, 'wb') as f:
        f.write(response.content)
    return img_path


def _save_actor_info(save_dir: str, name: str, info: dict):
    actor_dir = f'{save_dir}/{name}'
    os.makedirs(actor_dir, exist_ok=True)
    with open(f'{actor_dir}/info.json', 'w') as f:
        json.dump(info, f, indent=4)
