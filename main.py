# bot.py
import time
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel_id = 845742634244898836
    channel = await client.fetch_channel(channel_id)  # Use fetch_channel instead of get_channel

@client.event
async def on_message(message):
    print(message.content)
    # channel.send("Hello, this message is from the bot!")


client.run(TOKEN)
