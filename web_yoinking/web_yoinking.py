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

async def yoink_game(link:str, target_price:str)->dict:
            soup = getSoup(link) # get info on the page

            # Find game id and name
            title_image = soup.find("div", {"class": "col-left"}).find("div",{"class": "game-info-image-wrapper"}).find("img")
            game_image_url = title_image["src"]
            game_name = title_image["alt"]

            steampage_link = soup.find("a", {"class": "game-link-widget"})['href']
            steam_soup = getSoup(steampage_link)
            steam_price_element = steam_soup.find("div", {"class": "game_purchase_price price"})

            if steam_price_element is None:
                steam_price = steam_soup.find("div", {"class": "discount_original_price"}).text
            else:
                steam_price = steam_price_element.text
                steam_price = steam_price.replace('\n', '').replace('\t', '').replace('\u00a3', '')


            # Find historical low
            historical_low_tab = soup.find("div", {"id": "game-price-history-ranking"})
            historical_low_row = historical_low_tab.find("div", {"class": "game-content-box game-lowest-prices-content"}).find("div", {"class": "game-lowest-price-inner-row d-flex"})
            historical_low = historical_low_row.find("span", {"class": "inline-price price"}).text
            game_historical_low = historical_low.replace('~', '').replace('\u00a3', '')

            # Find game info
            official_store = soup.find("div", {"id": "official-stores"})

            # Find Best Key Price
            key_price = official_store.find("div", {"class": "relative price-info-with-label"}).find("a", {"class": "price game-price with-tooltip"}).text.replace('\u00a3', '')

            key_vendor_name = official_store.find("div", {"class": "relative hoverable-box d-flex flex-wrap flex-align-center game-item cta-full item game-deals-item game-list-item keep-unmarked-container"})['data-shop-name']

            key_vendor_url = official_store.find("a", {"class": "action-desktop-btn d-flex flex-align-center flex-justify-center action-btn cta-label-desktop with-arrows action-ext"})['href']
            key_vendor_url = "https://gg.deals"+key_vendor_url


            # ---- 'tracking_game_prices.json' ----

            return(
                {
                    "name": game_name,
                    "image_url": game_image_url,
                    "url": link,
                    "historical_low": game_historical_low,
                    "normal_price": steam_price,
                    "target_price": str(float(target_price)),
                    "price_track_key": key_price,
                    "price_track_key_vendor": key_vendor_name,
                    "price_track_key_url": key_vendor_url
                }
            )


async def yoink_games_info():
    tracking_list = await get_json_file("web_yoinking/tracking_game_list.json")
    game_tracking = []
    for tracking in tracking_list:
        game = tracking['name']

        link = "https://gg.deals/game/{}/".format(game) # each page of the website

        # return if page not found
        if await check_link_valid(link):
            game_tracking.append(await yoink_game(link, str(tracking['target_price']))) 

        with open('web_yoinking/tracking_game_prices.json', 'w') as json_file:
            json.dump(game_tracking, json_file, indent=4)
        

async def check_link_valid(link):
    soup = getSoup(link) # get info on the page

    try:
        ooops = soup.find("div", {"class": "col-left"}).find("div",{"class": "game-info-image-wrapper"}).find("img")
    except AttributeError:
        ooops = ""
    if ooops == "":
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


async def get_json_file(path:str):
    with open(path, 'r') as file:
        game_info = json.load(file)
    return game_info


async def add_game_track(name, price:str):
    tracking_info = await get_json_file("web_yoinking/tracking_game_list.json")
    formatted_name = await name_formatting(name)
    data = await yoink_game(f"https://gg.deals/game/{formatted_name}/", price)

    # check if game is already being tracked
    for game in tracking_info:
        if game['name'] == formatted_name:
            print(f"Game '{name}' is already being tracked.")
            return
    
    # edge case if game price is not int 
    if not isinstance(price, (int, float)) or price < 0:
        print(f"Price for '{name}' is not valid. Setting as historical low!")
        price = data['historical_low']

    tracking_info.append(
        {
            "name": formatted_name, 
            "target_price": price, 
            "full_name": data['name'], 
            "url": data['url']
         }
    )
    with open('web_yoinking/tracking_game_list.json', 'w') as file:
        json.dump(tracking_info, file, indent=4)


async def edit_game_track(name, price):
    tracking_info = await get_json_file("web_yoinking/tracking_game_list.json")
    for game in tracking_info:
        game_name = game['name']
        if game_name == name:
            game['target_price'] = int(price)
            with open('web_yoinking/tracking_game_list.json', 'w') as file:
                json.dump(tracking_info, file, indent=4)
            print(f"Game '{name}' has been updated to track at £{price}")
            return
        
if __name__ == "__main__":
    asyncio.run(yoink_games_info())