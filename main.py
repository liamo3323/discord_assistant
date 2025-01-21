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
        await asyncio.sleep(3600) # Sleep for 1 hour

#---------- GAME PRICE FUNCTIONS --------------

async def check_below_price():
    yoinked_info = await get_json_file("web_yoinking/tracking_game_prices.json")

    for yoinked in yoinked_info:
        target_price = float(yoinked['target_price'])
        price = float(yoinked['price_track_key'].replace("~", "").replace("\u00a3", ""))

        if target_price > price:
            print(f"{yoinked['name']} is below the set price of {yoinked['target_price']}")

            channel = await client.fetch_channel(845742634244898836)
            await channel.send(embed= await send_embed(yoinked))

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
    await init_update_feed()
    tracking_list = await get_json_file("manga_updates/tracking_chapter_list.json")

    for tracking in tracking_list:
        url = tracking['url']
        name = tracking['name']
        latest_chapter = tracking['latest_chap']
        updated_chapter = tracking['updated_chap']

        if latest_chapter != updated_chapter:
            print(f"New chapter for {name}!")

            embed = discord.Embed(title=name,description=f"",colour=0x00b0f4,timestamp=datetime.datetime.now())
            embed.add_field(name="New Chapter!",
                            value=f"{name}! - {updated_chapter}",
                            inline=False)
            embed.set_footer(text="Manga Tracking")
            channel = await client.fetch_channel(845742634244898836)
            await channel.send(embed=embed)

            tracking['latest_chap'] = updated_chapter
            with open('manga_updates/tracking_chapter_list.json', 'w') as file:
                json.dump(tracking, file, indent=4)

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
        tracking_data_file = await get_json_file("web_yoinking/tracking_game_prices.json")
        embed = discord.Embed(title="Currently Tracked Games Prices", colour=0x00b0f4, timestamp=datetime.datetime.now(), description="")

        good_deal_list = []
        value_list = []

        for tracking in tracking_data_file:
            tracking_price = tracking['price_track_key']
            vendor = tracking['price_track_key_vendor']
            original_price = tracking['normal_price']
            historical_low = tracking['historical_low']

            if await is_good_price(float(original_price.replace("~", "").replace("\u00a3", "")), float(tracking_price.replace("~", "").replace("\u00a3", "")), float(historical_low)):
                good_deal_list.append(f"**[{tracking['name']}]({tracking['url']})**\nCurrent Price - {tracking_price}\nVendor - {vendor}\n\nTracking Price - £{tracking['target_price']}\nHistorical low - £{tracking['historical_low']}\n-----------v------------\n")
            
            else:
                value_list.append(f"**[{tracking['name']}]({tracking['url']})**\nCurrent Price - {tracking_price}\nVendor - {vendor}\n\nTracking Price - £{tracking['target_price']}\nHistorical low - £{tracking['historical_low']}\n-----------------------\n")
                

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