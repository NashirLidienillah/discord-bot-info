import os
import discord
import google.generativeai as genai
import openai
import groq
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Konfigurasi Web Server (Keep-Alive) ---
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

# --- Muat Konfigurasi Bot & AI ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY') 

try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.0-pro')
except Exception as e:
    gemini_model = None
try:
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = None
except Exception as e:
    openai_client = None
try:
    if GROQ_API_KEY:
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
    else:
        groq_client = None
except Exception as e:
    groq_client = None

# --- Inisialisasi Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) 

@bot.event
async def on_ready():
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    
    try:
        guild = bot.guilds[0]
        member_count = guild.member_count
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} member di HEYN4S"
        )
        await bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"Status presence diupdate: {member_count} member.")
    
    except Exception as e:
        print(f"Gagal update presence saat on_ready: {e}")
        activity = discord.Activity(type=discord.ActivityType.listening, name="perintah !")
        await bot.change_presence(status=discord.Status.online, activity=activity)

# ---  FITUR BARU Monitor Member ---
@bot.event
async def on_member_join(member):
    """Dipanggil saat ada member baru masuk."""
    guild = member.guild
    member_count = guild.member_count
    
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"{member_count} member di HEYN4S"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Member baru bergabung, status diupdate: {member_count} member.")

@bot.event
async def on_member_leave(member):
    """Dipanggil saat ada member keluar."""
    guild = member.guild
    member_count = guild.member_count 
    
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"{member_count} member di HEYN4S"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Member keluar, status diupdate: {member_count} member.")

# --- Perintah Info (Prefix '!') ---
@bot.command(name="ping")
async def ping(ctx):
    latency_ms = round(bot.latency * 1000)
    await ctx.reply(f"Pong! 🏓\nLatensi saya {latency_ms} ms.")

@bot.command(name="rules")
async def rules(ctx):
    embed = discord.Embed(title="📜 Peraturan Server HEYN4S", description="Berikut adalah peraturan yang wajib dipatuhi:", color=discord.Color.gold())
    embed.add_field(name="1. Jaga Bahasa", value="Dilarang berkata kasar, SARA, atau mem-bully member lain.", inline=False)
    embed.add_field(name="2. Dilarang Spam", value="Jangan mengirim spam, promosi, atau link aneh di luar channel yang disediakan.", inline=False)
    embed.add_field(name="3. No NSFW", value="Dilarang keras memposting konten 18+.", inline=False)
    embed.add_field(name="4. Gunakan Channel Semestinya", value="Post di channel yang sesuai dengan topiknya.", inline=False)
    embed.set_footer(text="Terima kasih atas kerja samanya!")
    await ctx.reply(embed=embed)

@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="🤖 Bantuan Perintah Bot HEYN4S", description="Gunakan tanda seru `!` di depan perintah.\nContoh: `!ping`", color=discord.Color.blue())
    embed.add_field(name="Perintah Utilitas", value="• `!help`: Menampilkan pesan bantuan ini.\n• `!ping`: Cek kecepatan respons bot.\n• `!rules`: Menampilkan peraturan server.", inline=False)
    embed.add_field(name="Perintah AI", value="• `! [pertanyaan]`: Mengajukan pertanyaan ke AI.\n*(Contoh: `!siapa penemu listrik`)*\n\n**Status:** ⚠️ **(Sedang Dalam Perbaikan)**", inline=False)
    embed.set_footer(text="Bot HEYN4S v1.2")
    await ctx.reply(embed=embed)


# --- Fungsi on_message (AI) ---
@bot.event
async def on_message(message):
    if message.author == bot.user or isinstance(message.channel, discord.DMChannel):
        return
    await bot.process_commands(message)
    if message.content.startswith("!"):
        ctx = await bot.get_context(message)
        if ctx.command:
            return 
        embed = discord.Embed(
            title="⚙️ Fitur AI (Under Maintenance)",
            description="Maaf, fitur AI saat ini sedang dalam perbaikan dan tidak tersedia.\n\n"
                        "Kami sedang memperbaiki masalah koneksi API (Groq/Gemini/OpenAI). Mohon coba lagi nanti.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Terima kasih atas kesabaran Anda!")
        await message.reply(embed=embed)
        return
        # --- AKHIR PESAN MAINTENANCE ---

# --- Menjalankan Bot DAN Web Server ---
if TOKEN:
    start_keep_alive()
    bot.run(TOKEN)
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")