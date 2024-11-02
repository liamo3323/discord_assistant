# bot.py
import requests
import os
import discord
import logging
import yaml
import asyncio
import datetime
import pandas
import json

from web_yoinking import yoink_games_info, add_game_track, name_formatting, get_json_file, getSoup, check_link_valid
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)


async def loading_json():
    if os.path.exists('tracking_game_prices.json'):
        with open('tracking_game_prices.json', 'r') as file:
            game_info = json.load(file)
        print("tracking_game_prices.json loaded successfully")
        return game_info
    else:
        print("tracking_game_prices.json does not exist")


async def send_embed(game):
            embed = discord.Embed(title=game['name'],
                                url=game['url'],
                                description=f"Historical Low - £{game['historical_low']}",
                                colour=0x00b0f4,
                                timestamp=datetime.datetime.now())
            embed.set_author(name="Silver Wolf")
            embed.add_field(name=game['price_official_vendor'],
                            value=f"Official Keys - {game['price_official']}",
                            inline=False)
            embed.add_field(name=game['price_key_vendor'],
                            value=f"Key Price - {game['price_key']}",
                            inline=False)
            embed.set_image(url=game['image_url'])
            embed.set_footer(text="Game Price Tracking")
            return embed


async def check_below_price():
    tracking_info = await get_json_file("tracking_game_list.json")

    with open('tracking_game_prices.json', 'r') as file:
        yoinked_info = json.load(file)

    for x in range (len(tracking_info)):
        target_price = float(tracking_info[x]['target_price'])
        official_price = float(yoinked_info[x]['price_official'].replace("~", "").replace("\u00a3", ""))
        key_price = float(yoinked_info[x]['price_key'].replace("~", "").replace("\u00a3", ""))

        if target_price > official_price or target_price > key_price:
            print(f"{tracking_info[x]['name']} is below the set price of {tracking_info[x]['target_price']}")

            channel = await client.fetch_channel(845742634244898836)
            await channel.send(embed= await send_embed(yoinked_info[x]))


async def dailies():
    while True:
        print("Yoinking 'tracking_game_list' data...")
        await yoink_games_info()
        await asyncio.sleep(2)

        print("Checking for any price drops...")
        await check_below_price()
        
        #-------------------------------------------------------------------
        now = datetime.datetime.now()
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now > target_time:
            target_time += datetime.timedelta(days=1)
        delay = (target_time - now).total_seconds()

        hours, remainder = divmod(delay, 3600)
        minutes, _ = divmod(remainder, 60)
        print(f"Sleeping for {int(hours)} hours and {int(minutes)} minutes.")
        #-------------------------------------------------------------------
        await asyncio.sleep(delay)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # * start a timer till the set time to check for everything 


@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return


    if message.content == '!updates':
        game_info = await loading_json()
        for game in game_info:
            await message.channel.send(embed=await send_embed(game))


    if '!track' in message.content.lower():
        content = str(message.content).split()
        name = " ".join(content[1:-1])
        formatted_name = await name_formatting(name)
        price = content[len(content)-1]

        if await check_link_valid(getSoup("https://gg.deals/game/{}/".format(formatted_name))):
            await add_game_track(formatted_name, price)
            await message.channel.send(f"Game '{name}' has been added to the tracking list.")
        else:
            await message.channel.send(f"Game '{name}' could not be found.")

async def main():
    asyncio.create_task(dailies())
    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())