import os
from pyrogram import Client, filters
from pytube import Search
import yt_dlp

bot_token = os.getenv("BOT_TOKEN")
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

app = Client("BEATGURU", bot_token=bot_token, api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🎧 Welcome to *BEATGURU*!\nSend /play <song name> to listen to music.", quote=True)

@app.on_message(filters.command("play"))
async def play(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a song name after /play")
        return

    query = " ".join(message.command[1:])
    msg = await message.reply(f"🔍 Searching for: {query}")

    try:
        search = Search(query)
        video = search.results[0]
        url = video.watch_url
    except Exception as e:
        await msg.edit("❌ Couldn't find the song.")
        return

    await msg.edit(f"📥 Downloading: {video.title}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    os.makedirs("downloads", exist_ok=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

    await client.send_audio(
        chat_id=message.chat.id,
        audio=filename,
        title=info.get('title'),
        performer=info.get('uploader'),
        duration=int(info.get('duration')),
        caption=f"🎶 {info.get('title')}"
    )

    await msg.delete()
    os.remove(filename)

app.run()