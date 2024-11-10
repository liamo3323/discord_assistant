import os
import discord
import logging
import asyncio
import datetime
import json
import feedparser

from web_yoinking.web_yoinking import yoink_games_info, add_game_track, name_formatting, get_json_file, getSoup, check_link_valid, edit_game_track
from manga_updates.update_checker import init_update_feed, add_manga_track
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)



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


async def check_new_chapter():
    tracking_list = await get_json_file("tracking_chapter_list.json")
    tracking_data = await get_json_file("tracking_manga_info.json")

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
                    embed.set_author(name="Silver Wolf")
                    embed.add_field(name="New Chapter!",
                                    value=f"New chapter for {name}! - {latest_chapter}",
                                    inline=False)
                    embed.set_footer(text="Manga Tracking")
                    channel = await client.fetch_channel(845742634244898836)
                    await channel.send(embed=embed)

                    tracking_info['latest_chapter'] = latest_chapter
                    tracking_info['entries'] = entries

                    with open('tracking_manga_info.json', 'w') as json_file:
                        json.dump(tracking_data, json_file, indent=4)
                    break

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


@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return


    if message.content == '!updates':
        if os.path.exists("web_yoinking/tracking_game_prices.json"):
            with open("web_yoinking/tracking_game_prices.json", 'r') as file:
                game_info = json.load(file)
            print("tracking_game_prices.json loaded successfully")
        else:
            print("tracking_game_prices.json does not exist")

            for game in game_info:
                await message.channel.send(embed=await send_embed(game))


    if '!track_add' in message.content.lower():
        content = str(message.content).split()
        name = " ".join(content[1:-1])
        formatted_name = await name_formatting(name)
        price = content[len(content)-1]

        if await check_link_valid(getSoup("https://gg.deals/game/{}/".format(formatted_name))):
            await add_game_track(formatted_name, int(price))
            await message.channel.send(f"Game '{name}' has been added to the tracking list.")
        else:
            await message.channel.send(f"Game '{name}' could not be found.")
        
    if '!track_view' in message.content.lower():
        file = await get_json_file("web_yoinking/tracking_game_list.json")
        embed = discord.Embed(title="Currently Tracked Games Prices",
                    colour=0x00b0f4,
                    timestamp=datetime.datetime.now())
        embed.set_author(name="Silver Wolf")
        for game in file:
            value = f"[{game['full_name']}]({game['url']}) - {game['target_price']}"
            embed.add_field(name="",
                            value=value,
                            inline=False)
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

async def main():
    asyncio.create_task(dailies())
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())