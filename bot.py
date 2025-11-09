import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import start_keep_alive 

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) 

initial_cogs = [
    'cogs.events',
    'cogs.info',
    'cogs.utility'
    'cogs.admin'
]

print("Memuat cogs...")
for cog in initial_cogs:
    try:
        bot.load_extension(cog)
        print(f"  > Cog '{cog}' berhasil dimuat.")
    except Exception as e:
        print(f"  > GAGAL memuat cog '{cog}': {e}")
print("Semua cogs selesai dimuat.")

if TOKEN:
    start_keep_alive() 
    bot.run(TOKEN)     
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")