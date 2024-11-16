import discord
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from datetime import datetime
import json
import io

from credentials import credentials

DISCORD_TOKEN = credentials.get('DISCORD_TOKEN')
YOUTUBE_API_KEY = credentials.get('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = credentials.get('YOUTUBE_CHANNEL_ID') # ID do canal, não o nome de usuário
YOUTUBE_CHANNEL_NAME = credentials.get('YOUTUBE_CHANNEL_NAME')
DISCORD_CHANNEL_ID = credentials.get('DISCORD_CHANNEL_ID') # ID do canal do Discord

# Configurar Intents do Discord
intents = discord.Intents.default()
# Habilitar intents para guilds
intents.guilds = True
intents.members = True
# Habilitar intents para mensagens
intents.message_content = True

# Inicializa o cliente do Discord
bot = commands.Bot(command_prefix="!", intents=intents)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Arquivo para armazenar os IDs dos vídeos já anunciados
arquivo_videos_anunciados = "history_ids.json"

# Registra os logs
def log_register(message):
    moment = datetime.now()
    print(f"{moment} {message}\n")
    open("logs.txt", "a").write(f"{moment} {message}\n")

# Carrega os IDs dos vídeos já anunciados
try:
    with open(arquivo_videos_anunciados, "r") as f:
        videos_anunciados = set(json.load(f))
except FileNotFoundError:
    videos_anunciados = set()

@tasks.loop(minutes=1) # Verifica a cada 5 minutos - ajuste conforme necessário
async def verificar_novos_videos():
    try:
        request = youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            type="video",
            order="date", # Ordena por data para pegar o mais recente
            maxResults=1 # Pega apenas o vídeo mais recente
        )
        response = request.execute()

        if response['items']: # Verifica se há novos vídeos
            video_id = response['items'][0]['id']['videoId']

            # Verifica se o vídeo já foi anunciado
            if video_id not in videos_anunciados:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                canal_discord = bot.get_channel(DISCORD_CHANNEL_ID)

                await canal_discord.send(f"Novo vídeo! {video_url}")

                # Adiciona o ID do vídeo à lista de vídeos anunciados
                videos_anunciados.add(video_id)

                # Salva a lista atualizada em disco
                buffer = io.StringIO()
                json.dump(list(videos_anunciados), buffer)
                with open("dados.json", "w") as file:
                    file.write(buffer.getvalue())

                await canal_discord.send(f"@everyone Novo vídeo do {YOUTUBE_CHANNEL_NAME}! {video_url}")
            else:
                print(f"Novos vídeos não foram encontrados.")
    except Exception as error:
        print(f"Erro ao verificar vídeos: {error}")

@bot.event
async def on_ready():
    log_register(f"Bot conectado como {bot.user}")
    verificar_novos_videos.start()

# Rodar o bot
try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    log_register(f"Ocorreu um erro: {str(e)}")