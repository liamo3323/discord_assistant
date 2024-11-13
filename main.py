import os
import discord
import logging
import asyncio
import datetime
import json
import feedparser
import subprocess

from web_yoinking.web_yoinking import yoink_games_info, add_game_track, name_formatting, get_json_file, getSoup, check_link_valid, edit_game_track
from manga_updates.update_checker import init_update_feed, add_manga_track
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

#---------- DISCORD BOT FUNCTIONS -------------

async def dailies():
    # Command run before loop
    await init_update_feed()
    while True:
        print("Yoinking 'tracking_game_list' data...")
        await yoink_games_info()
        await asyncio.sleep(2)

        print("Checking for any price drops...")
        await check_below_price()
        await asyncio.sleep(2)
        
        print("Checking for any new chapters...")
        await check_new_chapter()
        await asyncio.sleep(2)

        # #-------------------------------------------------------------------
        # now = datetime.datetime.now()
        # target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        # if now > target_time:
        #     target_time += datetime.timedelta(days=1)
        # delay = (target_time - now).total_seconds()

        # hours, remainder = divmod(delay, 3600)
        # minutes, _ = divmod(remainder, 60)
        # print(f"Sleeping for {int(hours)} hours and {int(minutes)} minutes.")
        # #-------------------------------------------------------------------
        await asyncio.sleep(3600)

#---------- GAME PRICE FUNCTIONS --------------

async def check_below_price():
    tracking_info = await get_json_file("web_yoinking/tracking_game_list.json")

    with open("web_yoinking/tracking_game_prices.json", 'r') as file:
        yoinked_info = json.load(file)

    for x in range (len(tracking_info)):
        target_price = float(tracking_info[x]['target_price'])
        official_price = float(yoinked_info[x]['price_official'].replace("~", "").replace("\u00a3", ""))
        key_price = float(yoinked_info[x]['price_key'].replace("~", "").replace("\u00a3", ""))

        if target_price > official_price or target_price > key_price:
            print(f"{tracking_info[x]['name']} is below the set price of {tracking_info[x]['target_price']}")

            channel = await client.fetch_channel(845742634244898836)
            await channel.send(embed= await send_embed(yoinked_info[x]))

async def is_good_price(original_price, discounted_price, historical_low):
    # Calculate the discount percentage
    discount_percentage = await discount_price(original_price, discounted_price)

    # Define thresholds
    significant_discount_threshold = 50  # e.g., 50% discount
    close_to_historical_low_threshold = 0.2  # within 20% of historical low

    # Check if the discounted price is significantly lower than the original price
    is_significant_discount = discount_percentage >= significant_discount_threshold

    # Check if the discounted price is close to or lower than the historical low
    is_close_to_historical_low = discounted_price <= historical_low * (1 + close_to_historical_low_threshold)

    # Determine if the price is really good
    if is_significant_discount or is_close_to_historical_low:
        return True
    return False

async def discount_price(original_price, discounted_price):
    return (((original_price - discounted_price) / original_price) * 100)

async def send_embed(game):
            embed = discord.Embed(title=game['name'],
                                url=game['url'],
                                description=f"Historical Low - £{game['historical_low']}",
                                colour=0x00b0f4,
                                timestamp=datetime.datetime.now())
            embed.add_field(name=game['price_official_vendor'],
                            value=f"Official Keys - {game['price_official']}",
                            inline=False)
            embed.add_field(name=game['price_key_vendor'],
                            value=f"Key Price - {game['price_key']}",
                            inline=False)
            embed.set_image(url=game['image_url'])
            embed.set_footer(text="Game Price Tracking")
            return embed

#---------- MANGA TRACKING FUNCTIONS ----------

async def check_new_chapter():
    tracking_list = await get_json_file("manga_updates/tracking_chapter_list.json")
    tracking_data = await get_json_file("manga_updates/tracking_manga_info.json")

    for tracking in tracking_list:
        url = tracking['url']
        feed = feedparser.parse(url)

        name = feed['feed']['title'].replace(' - Releases on MangaUpdates', '')
        latest_chapter = feed['entries'][0]['title']
        entries = feed['entries']

        for tracking_info in tracking_data:
            if name == tracking_info['name']:
                if latest_chapter != tracking_info['latest_chapter']:
                    print(f"New chapter for {name}!")


                    embed = discord.Embed(title=name,
                    description=f"",
                    colour=0x00b0f4,
                    timestamp=datetime.datetime.now())
                    embed.add_field(name="New Chapter!",
                                    value=f"New chapter for {name}! - {latest_chapter}",
                                    inline=False)
                    embed.set_footer(text="Manga Tracking")
                    channel = await client.fetch_channel(845742634244898836)
                    await channel.send(embed=embed)

                    tracking_info['latest_chapter'] = latest_chapter
                    tracking_info['entries'] = entries
 
                    with open('manga_updates/tracking_manga_info.json', 'w') as json_file:
                        json.dump(tracking_data, json_file, indent=4)
                    break

#----------------------------------------------



@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    if '!track_add' in message.content.lower():
        content = str(message.content).split()
        name = " ".join(content[1:-1])
        formatted_name = await name_formatting(name)
        price = content[len(content)-1]

        if await check_link_valid("https://gg.deals/game/{}/".format(formatted_name)):
            await add_game_track(formatted_name, int(price))
            await message.channel.send(f"Game '{name}' has been added to the tracking list.")
        else:
            await message.channel.send(f"Game '{name}' could not be found.")
        
    if '!track_view' in message.content.lower():
        tracking_list_file = await get_json_file("web_yoinking/tracking_game_list.json")
        tracking_data_file = await get_json_file("web_yoinking/tracking_game_prices.json")
        embed = discord.Embed(title="Currently Tracked Games Prices", colour=0x00b0f4, timestamp=datetime.datetime.now(), description="")
        
        if len(tracking_list_file) == len(tracking_data_file):


            good_deal_list = []
            value_list = []
            for x in range(len(tracking_list_file)):
                discounted_price = tracking_data_file[x]['price_key']
                vendor = tracking_data_file[x]['price_key_vendor']
                original_price = tracking_data_file[x]['price_official']
                historical_low = tracking_data_file[x]['historical_low']

                if await is_good_price(float(original_price.replace("~", "").replace("\u00a3", "")), float(discounted_price.replace("~", "").replace("\u00a3", "")), float(historical_low)):
                    good_deal_list.append(f"**[{tracking_data_file[x]['name']}]({tracking_data_file[x]['url']})**\nCurrent Price - {discounted_price}\nVendor - {vendor}\n\nTracking Price - £{tracking_list_file[x]['target_price']}\nHistorical low - £{tracking_data_file[x]['historical_low']}\n-----------------------\n")
                
                else:
                    value_list.append(f"**[{tracking_data_file[x]['name']}]({tracking_data_file[x]['url']})**\nCurrent Price - {discounted_price}\nVendor - {vendor}\n\nTracking Price - £{tracking_list_file[x]['target_price']}\nHistorical low - £{tracking_data_file[x]['historical_low']}\n-----------------------\n")
                    

            if len(good_deal_list) != 0:
                embed.add_field(name="", value="🔥 Best Deals! 🔥", inline=False)
                for x in good_deal_list:
                    embed.add_field(name="", value=x, inline=False)
                
            embed.add_field(name="", value="Normal Deals",inline=False)
            
            for x in value_list:
                embed.add_field(name="", value=x, inline=False)
                
            await message.channel.send(embed=embed)

    if '!track_edit' in message.content.lower():
        content = str(message.content).split()
        name = " ".join(content[1:-1])
        formatted_name = await name_formatting(name)
        price = content[len(content)-1]
        await edit_game_track(formatted_name, int(price))
        await message.channel.send(f"Game '{name}' has been updated.")

    if '!manga_add' in message.content.lower():
        content = str(message.content).split()
        name = " ".join(content[1:-1])
        url = content[len(content)-1]
        await add_manga_track(name, url)
        await message.channel.send(f"Manga '{name}' has been added to the tracking list.")

    if '!manga_view' in message.content.lower():
        tracking_data = await get_json_file("manga_updates/tracking_manga_info.json")
        embed = discord.Embed(title="Currently Tracked Manga",
                    colour=0x00b0f4,
                    timestamp=datetime.datetime.now())
        for manga in tracking_data:
            embed.add_field(name="",
                            value=f"Latest Chapter - {manga['latest_chapter']}",
                            inline=False)
        await message.channel.send(embed=embed)

async def main():
    asyncio.create_task(dailies())
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())