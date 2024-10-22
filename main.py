# bot.py

import os
import discord
import logging
import yaml
import asyncio

from web_yoinking import get_games_info
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

async def web_yoink():
    print("Yoinking...")
    get_games_info()
    await asyncio.sleep(30)
    print("30 seconds later")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel_id = 845742634244898836
    channel = await client.fetch_channel(channel_id)  # Use fetch_channel instead of get_channel
    web_yoink()
    if os.path.exists('./game_info.yaml'):
        with open('./game_info.yaml', 'r') as file:
            game_info = yaml.safe_load(file)
        print("game_info.yaml loaded successfully")
    else:
        print("game_info.yaml does not exist")

@client.event
async def on_message(message):
    print(message.content)
    # channel.send("Hello, this message is from the bot!")


client.run(TOKEN)
