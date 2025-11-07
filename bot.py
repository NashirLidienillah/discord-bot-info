import os
import discord
import google.generativeai as genai
import openai
import groq
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
# --- Akhir Web Server ---

# --- Muat Konfigurasi Bot & AI ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY') 

try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.0-pro')
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI: {e}")
    gemini_model = None
try:
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("Model AI (OpenAI) berhasil dikonfigurasi.")
    else:
        openai_client = None
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi OpenAI: {e}")
    openai_client = None
try:
    if GROQ_API_KEY:
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
        print("Model AI (Groq) berhasil dikonfigurasi.")
    else:
        groq_client = None
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Groq: {e}")
    groq_client = None
# --- Akhir Konfigurasi ---


# --- Inisialisasi Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) 

@bot.event
async def on_ready():
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    activity = discord.Activity(type=discord.ActivityType.listening, name="perintah / dan !")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.slash_command(name="ping", description="Cek latensi dan status bot.")
async def ping(ctx: discord.ApplicationContext):
    latency_ms = round(bot.latency * 1000)
    await ctx.respond(f"Pong! 🏓\nLatensi saya {latency_ms} ms.")

@bot.slash_command(name="rules", description="Menampilkan peraturan server HEYN4S.")
async def rules(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="📜 Peraturan Server HEYN4S",
        description="Berikut adalah peraturan yang wajib dipatuhi:",
        color=discord.Color.gold()
    )
    embed.add_field(name="1. Jaga Bahasa", value="Dilarang berkata kasar, SARA, atau mem-bully member lain.", inline=False)
    embed.add_field(name="2. Dilarang Spam", value="Jangan mengirim spam, promosi, atau link aneh di luar channel yang disediakan.", inline=False)
    embed.add_field(name="3. No NSFW", value="Dilarang keras memposting konten 18+.", inline=False)
    embed.add_field(name="4. Gunakan Channel Semestinya", value="Post di channel yang sesuai dengan topiknya.", inline=False)
    embed.set_footer(text="Terima kasih atas kerja samanya!")
    await ctx.respond(embed=embed)

# --- ⬇️ FITUR BARU: Perintah /help ⬇️ ---
@bot.slash_command(name="help", description="Menampilkan daftar perintah bot.")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="🤖 Bantuan Perintah Bot HEYN4S",
        description="Berikut adalah daftar perintah yang bisa Anda gunakan:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Perintah Slash (/)", 
        value="Gunakan `/` untuk perintah utilitas server.\n\n"
              "• `/help`: Menampilkan pesan bantuan ini.\n"
              "• `/ping`: Cek kecepatan respons bot.\n"
              "• `/rules`: Menampilkan peraturan server.",
        inline=False
    )
    
    embed.add_field(
        name="Perintah AI (!)",
        value="Gunakan `!` untuk bertanya kepada AI.\n\n"
              "• `! [pertanyaan]`: Mengajukan pertanyaan ke AI.\n"
              "*(Contoh: `!siapa penemu listrik`)*\n\n"
              "**Status:** ⚠️ **(Sedang Dalam Perbaikan)**\n*Kami sedang memperbaiki koneksi API, mohon coba lagi nanti.*",
        inline=False
    )
    
    embed.set_footer(text="Bot HEYN4S v1.1")
    await ctx.respond(embed=embed)

# --- ⬆️ AKHIR FITUR  ⬆️ ---
@bot.event
async def on_message(message):
    if message.author == bot.user or isinstance(message.channel, discord.DMChannel):
        return

    # Cek 2: Jika pesan dimulai dengan '!', ini UNTUK AI
    if message.content.startswith("!"):
        
        # --- PESAN MAINTENANCE ---
        # Bot akan langsung balas ini dan berhenti.
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

        # -----------------------------------------------------------------
        # KODE AI LAMA DI BAWAH INI SEKARANG TIDAK AKAN PERNAH DIJALANKAN
        # KITA BIARKAN SAJA SAMPAI NANTI KITA PERBAIKI API-NYA
        # -----------------------------------------------------------------
        
        pertanyaan = message.content[1:].strip()
        if not pertanyaan:
            return

        async with message.channel.typing():
            jawaban_ai = None
            sumber_ai = "Tidak diketahui"
            error_log = {}

            # 1. Coba Groq
            if groq_client:
                try:
                    # (Kode Groq lama...)
                except Exception as e_groq:
                    # (Kode error Groq lama...)
                    pass # Abaikan saja

            # 2. Coba Gemini
            if jawaban_ai is None and gemini_model:
                try:
                    # (Kode Gemini lama...)
                except Exception as e_gemini:
                    # (Kode error Gemini lama...)
                    pass # Abaikan saja

            # 3. Coba OpenAI
            if jawaban_ai is None and openai_client:
                try:
                    # (Kode OpenAI lama...)
                except Exception as e_openai:
                    # (Kode error OpenAI lama...)
                    pass # Abaikan saja
            
            # ... (Sisa kode AI lama) ...

# --- ⬆️ AKHIR PERUBAHAN 3 ⬆️ ---


# --- Menjalankan Bot DAN Web Server ---
if TOKEN:
    start_keep_alive()
    bot.run(TOKEN)
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")