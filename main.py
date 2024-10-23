# bot.py

import os
import discord
import logging
import yaml
import asyncio
import datetime

from web_yoinking import get_games_info
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)


async def shutdown(ctx):
    await ctx.send("Shutting down...")
    await client.close()  # Gracefully close the bot



async def web_yoink():
    while True:
        print("Yoinking...")
        await get_games_info()
        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel_id = 845742634244898836
    channel = await client.fetch_channel(channel_id)  # Use fetch_channel instead of get_channel


    if os.path.exists('game_info.yaml'):
        with open('game_info.yaml', 'r') as file:
            game_info = yaml.load_all(file, Loader=yaml.FullLoader)
        print("game_info.yaml loaded successfully")
    else:
        print("game_info.yaml does not exist")


@client.event
async def on_message(message):
    print(message.content)

    if message.author == client.user:
        return

    if message.content == '!a':
        embed = discord.Embed(title="Game Price Tracking Added!",
                      description="GAME has been added to the list of tracked games!",
                      colour=discord.Color.blue(),
                      timestamp=datetime.datetime.now())

        embed.set_author(name="Silver Wolf")

        embed.set_footer(text="Game Price Tracking")

        await message.channel.send(embed=embed)

    else:
        await message.add_reaction('👍')

async def main():
    asyncio.create_task(web_yoink())
    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())