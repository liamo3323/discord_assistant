# bot.py
import os
import discord
import signal
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

def signal_handler(sig, frame):
    print("Recieved shutdown signal...")

    # Perform any cleanup actions here (e.g., logging out)
    # You can add any other cleanup tasks if necessary
    
    # Exit the program
    
    exit(0)

# Create an Intents object with all intents enabled
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

signal.signal(signal.SIGINT, signal_handler) # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler) # Handle termination signals

client.run(TOKEN)
