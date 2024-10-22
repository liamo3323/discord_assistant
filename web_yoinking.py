import time 

from bs4 import BeautifulSoup
import yaml
import requests


def getSoup(link):
    req = requests.get(link)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

def getSoup_headers(link, headers):
    req = requests.get(link, headers=headers)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_games_info():

    last_page = int((getSoup("https://gg.deals/games/?page=1").find("li", {"class": "page last-page with-spacer"}).find("a",{"aria-label": "Last page"}).text).strip("..."))
    for i in range(1, 2): #! UPDATE WHEN DEPLOYED
        game_ids = []
        game_names = []
        game_prices_int = []
        game_info = []

        link = "https://gg.deals/games/?page={}".format(i) # each page of the website

        soup = getSoup(link) # get info on the page
        soup = soup.find("div", {"class": "game-section"}) # find the div of the games


        games = soup.find_all("div", {"class": "hoverable-box"}) # find the div of each game
        for game in games:
            game_id = game["data-container-game-id"]
            game_ids.append(game_id)

            game_name = game["data-game-name"]
            game_names.append(game_name)

        game_prices = soup.find_all("div", {"class": "d-flex flex-align-center price-content"}) # find all "d-flex flex... on the html page"
        for price in game_prices:
            soup_price = (price.find("span", {"class": "price-inner numeric"})) # text price is within the div so search for "price-inner..." within the div
            price_formatted_str = soup_price.text.strip("~") # strip the annoying grave ~ 
            price = price_formatted_str.strip("£")
            price = 0 if price == "Free" else price
            game_prices_int.append(price)

    for i in range(len(game_ids)):
        x = { "name": game_names[i], "id": game_ids[i], "price_int": game_prices_int[i], "link": "https://gg.deals/game/{}".format(game_names[i]) }
        game_info.append(x)
    
    with open("game_info.yaml", "w") as f:
        yaml.dump_all(game_info, f)

if __name__ == "__main__":
    get_games_info()