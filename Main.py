import io
import json
import re
from datetime import datetime
from random import random

import discord
from discord.ext import commands, tasks
from googleapiclient.discovery import build

from credentials import credentials
from messages import messages

DISCORD_TOKEN = credentials.get('DISCORD_TOKEN')
YOUTUBE_API_KEY = credentials.get('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = credentials.get('YOUTUBE_CHANNEL_ID')
YOUTUBE_CHANNEL_NAME = credentials.get('YOUTUBE_CHANNEL_NAME')
DISCORD_CHANNEL_ID = credentials.get('DISCORD_CHANNEL_ID')

# Configure Discord intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

# Initialize Discord bot
bot = commands.Bot(command_prefix="!", intents=intents)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# File to store announced video IDs
ANNOUNCED_VIDEOS_FILE = "history_ids.json"

# Set of announced video IDs
announced_videos = set()


# Log messages
def log_register(message):
  timestamp = datetime.now()
  print(f"{timestamp} {message}")
  with open("logs.txt", "a", encoding="utf-8") as file:
    file.write(f"{timestamp} {message}\n")


# Load announced video IDs
try:
  with open(ANNOUNCED_VIDEOS_FILE, "r", encoding="utf-8") as f:
    announced_videos = set(json.load(f))
except FileNotFoundError:
  announced_videos = set()
  log_register(f"O arquivo {ANNOUNCED_VIDEOS_FILE} não foi encontrado")
except json.JSONDecodeError:
  log_register("JSONDecodeError: provavelmente o arquivo JSON está vazio.")
  announced_videos = set()


@tasks.loop(minutes=0.5)  # Check every 0.5 minutes - adjust as needed
async def check_for_new_videos():
  try:
    request = youtube.search().list(
      part="snippet",
      channelId=YOUTUBE_CHANNEL_ID,
      type="video",
      order="date",  # Order by date to get the most recent video
      maxResults=1  # Get only the most recent video
    )
    response = request.execute()

    discord_channel = bot.get_channel(DISCORD_CHANNEL_ID)

    if not discord_channel:
      log_register(f"Canal com ID {DISCORD_CHANNEL_ID} não encontrado.")
      return

    if response['items']:  # Check if there are new videos
      video_id = response['items'][0]['id']['videoId']

      # Check if the video has already been announced
      if video_id not in announced_videos:
        log_register(f"ID do Vídeo atual: {video_id}. O ID atual não estava nos IDs anteriores.")

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_title = response['items'][0]['snippet']['title']

        # Tratamento do video_title, removendo caracteres tipo &quot; &copy; com regex
        video_title = re.sub(r'&[a-zA-Z]+;', '', video_title)

        if messages:
          message = messages[int(random() * len(messages))]
          if message:
            if "{username}" in message:
              message = message.format(username=YOUTUBE_CHANNEL_NAME)
          else:
            message = f"Vídeo novo do {YOUTUBE_CHANNEL_NAME}! Assista aqui:"
        else:
          message = f"Vídeo novo do {YOUTUBE_CHANNEL_NAME}! Assista aqui:"

        message = message.encode('charmap', errors='replace').decode('charmap')

        announcement = f"@everyone {message.strip()} - {video_title}! {video_url}"
        await discord_channel.send(announcement)

        log_register(f"Mensagem: {announcement}")
        log_register(f"Mensagem de aviso de Vídeo enviada!")

        # Add the video ID to the set of announced videos
        announced_videos.add(video_id)

        # Save the updated set to disk
        buffer = io.StringIO()
        json.dump(list(announced_videos), buffer)
        with open(ANNOUNCED_VIDEOS_FILE, "w", encoding="utf-8") as file:
          file.write(buffer.getvalue())
      else:
        print(f"Novos vídeos do {YOUTUBE_CHANNEL_NAME} não foram encontrados.")
  except Exception as error:
    log_register(f"Erro ao verificar vídeos: {error}")


@bot.event
async def on_ready():
  log_register(f"Bot conectado como {bot.user}")
  check_for_new_videos.start()


# Run the bot
try:
  bot.run(DISCORD_TOKEN)
except Exception as e:
  log_register(f"Ocorreu um erro: {str(e)}")
