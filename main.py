import os
import requests
import re
import yaml
import sys
import logging
from time import sleep

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s %(message)s",
)

URL = "https://onepiecechapters.com"
DATA_FILE = "data.yaml"
DOWNLOAD_FOLDER = "data"


def read_yaml():
    with open(DATA_FILE, "r") as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        data = yaml.safe_load(file)

        return data


def get_saved_chapter():
    return read_yaml()["latest"]


def write_saved_chapter(num: int):
    data = read_yaml()
    with open(DATA_FILE, "w") as file:
        data["latest"] = num
        yaml.dump(data, file)


def get_latest_chapter():
    r = requests.get(URL)
    text = r.text
    text = text.splitlines()

    tag = ""
    for t in text:
        if "One Piece Chapter " in t:
            tag = t
            break

    chapter_num = re.search('One Piece Chapter (.+?)" ', tag).group(1)
    chapter_path = re.search('href="(.+?)">', tag).group(1)
    chapter_url = URL + chapter_path

    return {"num": chapter_num, "url": chapter_url}


def download_chapter(chapter: dict):
    num = chapter["num"]
    url = chapter["url"]
    folder = f"{DOWNLOAD_FOLDER}/Chapter {num}"
    r = requests.get(url)
    os.makedirs(folder)
    text = r.text
    text = text.splitlines()

    num = 1

    pages = [item for item in text if "cdn.onepiecechapters.com" in item]
    for t in pages:
        aux = re.search('src="(.+?)" ', t).group(1)
        img = requests.get(aux).content
        with open(f"{folder}/page{num}.png", "wb") as handler:
            handler.write(img)
        num += 1


if "-s" in sys.argv:
    log = logging.getLogger("main")
    while True:
        latest_chapter = get_latest_chapter()
        num = latest_chapter["num"]
        url = latest_chapter["url"]

        if get_saved_chapter() == num:
            log.info("No new update")
        else:
            log.info(f"New chapter {num} available")
            log.info(f"Downloading chapter {num}")
            download_chapter(latest_chapter)
            log.info(latest_chapter["url"])
            write_saved_chapter(num)

        sleep(60 * 60)


else:
    latest_chapter = get_latest_chapter()
    num = latest_chapter["num"]
    url = latest_chapter["url"]

    if get_saved_chapter() == num:
        print("No new update")
    else:
        print(f"New chapter {num} available")
        print(f"Downloading chapter {num}")
        download_chapter(latest_chapter)
        print(latest_chapter["url"])
        write_saved_chapter(num)
