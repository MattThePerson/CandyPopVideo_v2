import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
# from http.cookiejar import MozillaCookieJar
from urllib.parse import unquote

from config import ACTOR_INFO_DIR


REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# REQUEST_COOKIES = MozillaCookieJar('cookies.txt')
# REQUEST_COOKIES.load()

#region - PUBLIC -------------------------------------------------------------------------------------------------------


def get_actor_info(name):
    
    info_file = f'{ACTOR_INFO_DIR}/{name}/info.json'
    
    if not os.path.exists(info_file):
        return None
    
    with open(info_file, 'r') as f:
        info = json.load(f)
    
    if info is None or info == {}:
        return None
    
    return info
    



def fetch_actor_info(name):
    
    info = _scrape_actor_info(name, ACTOR_INFO_DIR, download_media=True)
    
    return info



#region - PRIVATE ------------------------------------------------------------------------------------------------------

def _scrape_actor_info(name, save_dir, download_media=True) -> dict|None:
    
    info = {
        'name': name,
        'date_of_birth': None,
        'galleries': [],
    }

    info_bp = _scrape_babepedia(name, save_dir, download_media=download_media)
    if info_bp is None:
        return None
    
    if 'Born' in info_bp:
        info['date_of_birth'] = _format_date_of_birth(info_bp['Born'])
    info['babepedia'] = info_bp
    
    # save json
    _save_actor_info(save_dir, name, info)
        
    # download media
    if download_media and info_bp['galleries']:
        gall_paths = _download_actor_galleries(save_dir, name, info_bp['galleries'])
        info['galleries'] = gall_paths
        _save_actor_info(save_dir, name, info)
    
    return info


# HELPERS

def _scrape_babepedia(name, save_dir, download_media=True) -> dict|None:
    # step 1: get soup
    res = _get_babepedia_page_by_name(name)
    res.raise_for_status()
    
    if '/search/' in res.url:
        print('No such babe in babepedia:', name)
        return None

    soup = BeautifulSoup(res.content, 'html.parser')
    
    # extract babepedia info
    info = _parse_babepedia_info(soup)
    info = {'url': res.url} | info
    return info


def _get_babepedia_page_by_name(name):
    
    url = 'https://www.babepedia.com/babe/' + name.replace(' ', '_')
    # res = requests.get(url, cookies=COOKIES, headers=REQUEST_HEADERS)
    print('requesting:', url)
    res = requests.get(url, headers=REQUEST_HEADERS)
    return res


def _parse_babepedia_info(soup):
    info = {}
    # get info
    info['last_scraped'] = str(datetime.now())[:10]
    
    info = info | _get_personal_info(soup)
    
    try:
        info['bio'] = soup.select_one('#biotext').text
    except:
        print('Unable to get "bio"')
    
    try:
        info['aka'] = soup.select_one('#aka').text.replace('Also known as: ', '').replace('\xa0', '').split(' - ')
    except:
        print('Unable to get "aka"')
    
    comments = _get_bp_comments(soup)
    if comments:
        info['comments'] = comments
    
    # get image hrefs
    galls = []
    for gall in soup.select('.gallery'):
        for a_el in gall.select('a'):
            # print(a_el['href'])
            galls.append(a_el['href'])
    info['galleries'] = galls
    
    return info

# Selector for info items: '#personal-info-block .info-item:not(.info-title)'
def _get_personal_info(soup):
    info_items = soup.select('#personal-info-block .info-item:not(.info-title)')
    info = {}
    for info_item in info_items:
        label = info_item.select_one('.label').text
        value = info_item.select_one('.value').text
        info[label.replace(':', '')] = value
    return info

def _format_date_of_birth(born):
    parts = born.split()
    day = ''.join(filter(str.isdigit, parts[1]))  # Remove suffix from day
    cleaned = f"{parts[0]} {day} of {parts[3]} {parts[4]}"
    dt = datetime.strptime(cleaned, '%A %d of %B %Y')
    return dt.strftime('%Y-%m-%d')

def _get_bp_comments(soup):
    comment_els = soup.select('.commentbox .comment')
    if comment_els:
        comments = [ 
            comment_el.text for comment_el in comment_els
        ]
        return comments
    return None

def _download_actor_galleries(save_dir, name, galleries, redo=False):
    RELATIVE_BASE = f'{name}/media/babepedia'
    paths = []
    for idx, gall in enumerate(galleries):
        url = 'https://www.babepedia.com' + gall
        img_path = f'{save_dir}/{RELATIVE_BASE}{unquote(gall)}'
        print('({}/{}) downloading image from: "{}"  ->  "{}"'.format(idx+1, len(galleries), url, gall))
        if redo or not os.path.exists(img_path):
            try:
                ret = _download_image(url, img_path)
            except requests.HTTPError as err:
                print('HTTPError:', err)
        if os.path.exists(img_path):
            paths.append( img_path.replace(save_dir, '') )
    return paths

def _download_image(url, img_path):
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.raise_for_status()  # Raises HTTPError for bad responses
    with open(img_path, 'wb') as f:
        f.write(response.content)
    return img_path

def _save_actor_info(save_dir, name, info):
    ACTOR_DIR = save_dir + '/' + name
    os.makedirs(ACTOR_DIR, exist_ok=True)
    info_file = ACTOR_DIR + '/' + 'info.json'
    with open(info_file, 'w') as f:
        json.dump(info, f, indent=4)


