import time 

from bs4 import BeautifulSoup
import json
import requests
import asyncio
import re


def getSoup(link):
    req = requests.get(link)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

async def get_games_info(game:str = "metaphor-refantazio"):

    game_name = ""
    game_image_url = ""
    game_historical_low = ""

    game_price_official = ""
    game_price_official_vendor = ""
    game_price_official_url = ""

    game_price_key = ""
    game_price_key_vendor = ""
    game_price_key_url = ""

    link = "https://gg.deals/game/{}/".format(game) # each page of the website

    soup = getSoup(link) # get info on the page

    # return if page not found
    try:
        ooops = soup.find("div", {"class": "error-content"}).find("div", {"class": "title"}).text
    except AttributeError:
        ooops = ""

    if ooops == "Oooops!":
            return
    
    # Find game id and name
    title_image = soup.find("img", {"class": "image-game"})
    game_image_url = title_image["src"]
    game_name = title_image["alt"]

    # Find game historical low
    historical_low_col = soup.find("div", {"class": "relative game-info-price-col historical game-header-price-box lowest-recorded expired"})
    game_historical_low = historical_low_col.find("span", {"class": "price-inner numeric"}).text

    # Find game official price
    hoverable_box = soup.find_all("div", {"class": "load-more-content shadow-box-big-light"})
    game_price_official_vendor = hoverable_box[0].find("div", {"class": "relative hoverable-box d-flex flex-wrap flex-align-center game-item cta-full item game-deals-item game-list-item keep-unmarked-container"})['data-shop-name']
    game_price_official_url = "https://gg.deals{}/".format(hoverable_box[0].find("a", {"class": "d-flex flex-align-center shop-link"})["href"])
    game_price_official = hoverable_box[0].find("a", {"class": "price game-price with-tooltip"}).find("span", {"class": "price-inner"}).text

    # Find game key price
    game_price_key_vendor = hoverable_box[1].find("div", {"class": "relative hoverable-box d-flex flex-wrap flex-align-center game-item cta-full item game-deals-item game-list-item keep-unmarked-container"})['data-shop-name']
    game_price_key_url = "https://gg.deals{}/".format(hoverable_box[1].find("a", {"class": "d-flex flex-align-center shop-link"})["href"])
    game_price_key = hoverable_box[1].find("a", {"class": "price game-price with-tooltip"}).find("span", {"class": "price-inner"}).text

    game_tracking = [
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
    ]

    # try:
    #     with open('tracking_game_prices.json', 'r') as json_file:
    #         existing_games = json.load(json_file)  
    # except FileNotFoundError:
    #     existing_games = []

    # existing_games.append(game_tracking)

    # with open('tracking_game_prices.json', 'w') as json_file:
    #     json.dump(existing_games, json_file, indent=4)


    with open('tracking_game_prices.json', 'w') as json_file:
        json.dump(game_tracking, json_file, indent=4)

async def name_formatting(name:str):
     # remove mention of PC from game name
     # remove special characters
     # replace spaces with hiphens

    name = re.sub(r'\bPC\b', '', name)  # remove mention of PC
    name = re.sub(r'\bEdition\b', '', name)  # remove mention of PC
    name = re.sub(r'[^a-zA-Z0-9\s-]', '', name)  # remove special characters
    name = re.sub(r'\s+', '-', name)  # replace spaces with hyphens
    name = name.strip('-')  # remove leading/trailing hyphens
    return name.lower()  # return in lowercase

if __name__ == "__main__":
    asyncio.run(get_games_info())