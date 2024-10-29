import os 
import json
import requests
import asyncio
import re

from bs4 import BeautifulSoup

def getSoup(link):
    req = requests.get(link)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup


async def yoink_games_info():
    tracking_list = await get_name_list()
    game_tracking = []
    for tracking in tracking_list:
        game = tracking['name']

        link = "https://gg.deals/game/{}/".format(game) # each page of the website
        soup = getSoup(link) # get info on the page

        # return if page not found
        if await link_valid(soup):

            # Find game id and name
            title_image = soup.find("div", {"class": "col-left"}).find("div",{"class": "game-info-image-wrapper"}).find("img")
            game_image_url = title_image["src"]
            game_name = title_image["alt"]

            # Find official historical low
            historical_low = soup.find_all("div", {"class": "relative game-info-price-col historical game-header-price-box lowest-recorded expired"}) 

            official_historical_low = historical_low[0].find("span", {"class": "price-inner numeric"}).text.replace('~', '').replace('\u00a3', '')
            key_historical_low = historical_low[1].find("span", {"class": "price-inner numeric"}).text.replace('~', '').replace('\u00a3', '')

            game_historical_low = min(float(official_historical_low), float(key_historical_low))

            # Find game official price
            hoverable_box = soup.find_all("div", {"class": "load-more-content shadow-box-big-light"})
            game_price_official_vendor = hoverable_box[0].find("div", {"class": "relative hoverable-box d-flex flex-wrap flex-align-center game-item cta-full item game-deals-item game-list-item keep-unmarked-container"})['data-shop-name']
            game_price_official_url = "https://gg.deals{}/".format(hoverable_box[0].find("a", {"class": "d-flex flex-align-center shop-link"})["href"])
            game_price_official = hoverable_box[0].find("a", {"class": "price game-price with-tooltip"}).find("span", {"class": "price-inner"}).text

            # Find game key price
            game_price_key_vendor = hoverable_box[1].find("div", {"class": "relative hoverable-box d-flex flex-wrap flex-align-center game-item cta-full item game-deals-item game-list-item keep-unmarked-container"})['data-shop-name']
            game_price_key_url = "https://gg.deals{}/".format(hoverable_box[1].find("a", {"class": "d-flex flex-align-center shop-link"})["href"])
            game_price_key = hoverable_box[1].find("a", {"class": "price game-price with-tooltip"}).find("span", {"class": "price-inner"}).text

            game_tracking.append(
                {
                    "name": game_name,
                    "image_url": game_image_url,
                    "historical_low": game_historical_low,
                    "price_official": game_price_official,
                    "price_official_vendor": game_price_official_vendor,
                    "price_official_url": game_price_official_url,
                    "price_key": game_price_key,
                    "price_key_vendor": game_price_key_vendor,
                    "price_key_url": game_price_key_url,
                    "url": link
                }
            )

        with open('tracking_game_prices.json', 'w') as json_file:
            json.dump(game_tracking, json_file, indent=4)
        

async def link_valid(soup):
    try:
        ooops = soup.find("div", {"class": "col-left"}).find("div",{"class": "game-info-image-wrapper"}).find("img")
    except AttributeError:
        ooops = ""
    if ooops == "":
        print("Page not found")
        return False
    else:
        return True


async def name_formatting(name:str):
     # remove mention of PC and Edition from game name
     # remove special characters
     # replace spaces with hiphens

    name = re.sub(r'\bPC\b', '', name)  # remove mention of PC
    name = re.sub(r'\bEdition\b', '', name)  # remove mention of PC
    name = re.sub(r'[^a-zA-Z0-9\s-]', '', name)  # remove special characters
    name = re.sub(r'\s+', '-', name)  # replace spaces with hyphens
    name = name.strip('-')  # remove leading/trailing hyphens
    return name.lower()  # return in lowercase


async def get_name_list():
    with open('tracking_game_list.json', 'r') as file:
        game_info = json.load(file)
    return game_info


async def add_game_track(name, price):
    game_info = await get_name_list()
    formatted_name = await name_formatting(name)
    
    for game in game_info:
        if game['name'] == formatted_name:
            print(f"Game '{name}' is already being tracked.")
            return
        
    game_info.append({"name": formatted_name, "target_price": price})
    with open('tracking_game_list.json', 'w') as file:
        json.dump(game_info, file, indent=4)


if __name__ == "__main__":
    # asyncio.run(add_game_track("Another Crab's Treasure PC Edition", 25))
    asyncio.run(yoink_games_info())