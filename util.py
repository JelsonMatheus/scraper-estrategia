from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import os, time, random, json, requests


def load_json(name):
    if os.path.isfile(name):
        f = open(name, encoding='utf-8')
        data = json.load(f)
        f.close()
        return data
    else:
        return {}

def save_json(name:str, data:dict):
    with open(name, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

def sleep(a, b):
    time.sleep(random.randint(a, b))


def clean_name(name:str):
    char_remove = ['.', ':', '"', '”', '>', '<', '?', '|']
    name = name.replace('/', '-')
    for char in char_remove:
        name = name.replace(char, '')
    return name.strip()[:122]


def clean_name_file(name):
    return clean_name(name)[:54]


def create_course_path(root, name):
    path = Path(root) / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_file(url, filepath):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    }
    s = requests.session()
    s.headers.update(headers)
    response = s.get(url)
    file = open(filepath, 'wb')
    file.write(response.content)
    file.close()


def check_already_file(filepath):
    return os.path.isfile(filepath)