import os
import discord
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Bot AI sedang aktif."
def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
def start_keep_alive():
    t = Thread(target=run_server)
    t.start()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI. Periksa GEMINI_API_KEY Anda.")
    model = None

intents = discord.Intents.default()
intents.message_content = True  

# prefix '!'
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Dipanggil ketika bot berhasil terhubung ke Discord."""
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    activity = discord.Activity(type=discord.ActivityType.listening, name="perintah !")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    if model:
        print("Bot AI tanya-jawab siap digunakan.")
    else:
        print("PERINGATAN: Bot online, tapi fitur AI tidak aktif.")

@bot.event
async def on_message(message):
    """Dipanggil setiap kali ada pesan baru masuk."""

    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        return
    if message.content.startswith("!"):
        pertanyaan = message.content[1:].strip()
        if not pertanyaan:
            return
        if not model:
            await message.reply("Maaf, layanan AI sedang tidak terkonfigurasi. Hubungi admin.")
            return
        async with message.channel.typing():
            try:
                response = await model.generate_content_async(pertanyaan)
                embed = discord.Embed(
                    title="🤔 Pertanyaan Anda:",
                    description=f"```{pertanyaan}```",
                    color=discord.Color.blue()
                )
                
                jawaban_ai = response.text[:4000]
                embed.add_field(
                    name="🤖 Jawaban AI:",
                    value=jawaban_ai,
                    inline=False
                )
                embed.set_footer(text=f"Dijawab untuk: {message.author.display_name}")
                await message.reply(embed=embed)

            except Exception as e:
                print(f"Error saat memanggil Gemini API: {e}")
                await message.reply(
                    f"Maaf, terjadi kesalahan saat memproses pertanyaanmu.\n`Error: {e}`"
                )
    await bot.process_commands(message)
if TOKEN:
    start_keep_alive()
    bot.run(TOKEN)      
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")