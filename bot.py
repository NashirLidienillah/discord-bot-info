import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import start_keep_alive # Import server Flask kita

# Muat Konfigurasi Bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Inisialisasi Bot dengan Intents
intents = discord.Intents.default()
intents.message_content = True  # Untuk membaca !perintah
intents.members = True          # Untuk menghitung member

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) 

# Daftar 'Cogs' (fitur) yang akan dimuat
# Ini adalah nama file di dalam folder 'cogs'
initial_cogs = [
    'cogs.events',
    'cogs.info',
    'cogs.utility'
]

# Memuat semua Cogs
print("Memuat cogs...")
for cog in initial_cogs:
    try:
        bot.load_extension(cog)
        print(f"  > Cog '{cog}' berhasil dimuat.")
    except Exception as e:
        print(f"  > GAGAL memuat cog '{cog}': {e}")
print("Semua cogs selesai dimuat.")

# Menjalankan Bot DAN Web Server
if TOKEN:
    start_keep_alive() # Menjalankan server web
    bot.run(TOKEN)     # Menjalankan bot
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")