import feedparser
import requests
import asyncio
import json 
import os

from bs4 import BeautifulSoup

def getSoup(link):
    req = requests.get(link)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

async def get_json_file(path:str):
    with open(path, 'r') as file:
        game_info = json.load(file)
    return game_info

async def init_update_feed():

    chapter_info = []
    tracking_list = await get_json_file("manga_updates/tracking_chapter_list.json")

    for tracking in tracking_list:
        url = tracking['url']
        name = tracking['name']
        soup = getSoup(url)
        site = await checK_website(url)
        if site == "mangaplus":
            online_chapter = soup.find_all("div", {"class": "ChapterListItem-module_chapterListItem_ykICp"})
        elif site == "asuracomic":
            online_chapter = soup.find("div", {"class": "grid grid-cols-2 px-4 py-4 gap-2.5"}).find_all("h3", {"class": "font-bold text-xl"})[1].find("span", {"class": "pl-[1px]"}).text
        elif site == "weebcentral": # *DONE*
            online_chapter = soup.find("span", {"class": "grow flex items-center gap-2"}).find("span",{"class": ""}).text
        else:
            online_chapter = "-1"

        chapter_info.append(
            {
                "name": name,
                "url": url,
                "latest_chap": "0",
                "updated_chap": online_chapter
            }
        )
    with open('manga_updates/tracking_chapter_list.json', 'w') as file:
        json.dump(chapter_info, file, indent=4)

async def add_manga_track(name, url):
    tracking_list = await get_json_file("manga_updates/tracking_chapter_list.json")
    tracking_list.append(
        {
            "name": name,
            "url": url,
            "latest_chap": "0",
            "updated_chap": "-1"
        }
    )

    with open('manga_updates/tracking_chapter_list.json', 'w') as json_file:
        json.dump(tracking_list, json_file, indent=4)

async def checK_website(url)-> str:
    if "mangaplus" in url:
        return "mangaplus" 
    elif "asuracomic" in url:
        return "asuracomic"
    elif "weebcentral" in url:
        return "weebcentral"
    else:
        return None

if __name__ == "__main__":
    asyncio.run(add_manga_track("The Beginning After the End", "https://weebcentral.com/series/01J76XYE23859ZWDP7BJ520AKY/The-Beginning-After-The-End"))
    asyncio.run(add_manga_track("Reformation of the Deadbeat Noble", "https://asuracomic.net/series/reformation-of-the-deadbeat-noble-a624fb66"))
    asyncio.run(add_manga_track("Solo Leveling: Ragnarok", "https://asuracomic.net/series/solo-leveling-ragnarok-ded5d1c6"))
    asyncio.run(add_manga_track("Chainsaw Man", "https://weebcentral.com/series/01J76XYCRVY3QGYAMRR3STW941/Chainsaw-Man"))
    asyncio.run(init_update_feed())


    # {
    #     "name": "Mato Seihei no Slave",
    #     "url": "https://api.mangaupdates.com/v1/series/24893347544/rss"
    # },
    # {
    #     "name": "Rebuild World",
    #     "url": "https://api.mangaupdates.com/v1/series/73393743472/rss"
    # },
    # {
    #     "name": "The Lazy Lord Masters the Sword",
    #     "url": "https://api.mangaupdates.com/v1/series/43476221806/rss"
    # },
    # {
    #     "name": "Kaijuu 8",
    #     "url": "https://api.mangaupdates.com/v1/series/19101650311/rss"
    # },
    # {
    #     "name": "Chainsaw Man",
    #     "url": "https://api.mangaupdates.com/v1/series/75336092483/rss"
    # },
    # {
    #     "name": "Eleceed",
    #     "url": "https://api.mangaupdates.com/v1/series/10076623491/rss"
    # },