# bot.py

import os
import discord
import logging
import yaml
import asyncio
import datetime
import pandas
import json

from web_yoinking import yoink_games_info, add_game_track, name_formatting, link_valid
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

async def shutdown(ctx):
    await ctx.send("Shutting down...")
    await client.close()  # Gracefully close the bot

async def load_channel():
    await client.fetch_channel(845742634244898836)

async def web_yoink():
    while True:
        print("Yoinking...")
        await yoink_games_info()
        await asyncio.sleep(3)
        await loading_json()
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await load_channel()


@client.event
async def on_message(message):
    print(message.content)

    if message.author == client.user:
        return

    if message.content == '!updates':
        game_info = await loading_json()
        for game in game_info:
            print(game)
            embed = discord.Embed(title=game[0]['name'],
                                url=game[0]['url'],
                                description=f"Historical Low - {game[0]['historical_low']}",
                                colour=0x00b0f4,
                                timestamp=datetime.datetime.now())
            embed.set_author(name="Silver Wolf")
            embed.add_field(name=game[0]['price_official_vendor'],
                            value=f"Official Keys - {game[0]['price_official']}",
                            inline=False)
            embed.add_field(name=game[0]['price_key_vendor'],
                            value=f"Key Price - {game[0]['price_key']}",
                            inline=False)
            embed.set_image(url=game[0]['image_url'])
            embed.set_footer(text="Game Price Tracking")
            await message.channel.send(embed=embed)

    if '!track' in message.content.lower():
        # !track Another Crab's Treasure PC 25
        content = str(message.content).split()
        name = " ".join(content[1:-1])
        formatted_name = await name_formatting(name)
        price = content[len(content)-1]
        await add_game_track(formatted_name, price)
        await message.channel.send(f"Game '{name}' has been added to the tracking list.")

async def main():
    asyncio.create_task(web_yoink())
    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())