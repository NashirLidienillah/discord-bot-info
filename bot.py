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
# (Ini biarkan saja, sudah benar)
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
# (Ini semua biarkan saja, sudah benar)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY') 

# --- Konfigurasi AI (Gemini) ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.0-pro') # Model stabil
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI: {e}")
    gemini_model = None

# --- Konfigurasi AI (Groq) ---
try:
    if GROQ_API_KEY:
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
        print("Model AI (Groq) berhasil dikonfigurasi.")
    else:
        groq_client = None
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Groq: {e}")
    groq_client = None

# --- Konfigurasi AI (OpenAI) ---
try:
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("Model AI (OpenAI) berhasil dikonfigurasi.")
    else:
        openai_client = None
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi OpenAI: {e}")
    openai_client = None
# --- Akhir Konfigurasi ---


# --- Inisialisasi Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Jangan lupa ini untuk member count
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) 

# --- Event Bot (on_ready, member join/leave) ---
@bot.event
async def on_ready():
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    try:
        guild = bot.guilds[0]
        member_count = guild.member_count
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} member di HEYN4S")
        await bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"Status presence diupdate: {member_count} member.")
    except Exception as e:
        print(f"Gagal update presence saat on_ready: {e}")

@bot.event
async def on_member_join(member):
    guild = member.guild
    member_count = guild.member_count
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} member di HEYN4S")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Member baru bergabung, status diupdate: {member_count} member.")

@bot.event
async def on_member_leave(member):
    guild = member.guild
    member_count = guild.member_count
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} member di HEYN4S")
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
    embed.add_field(name="Perintah AI", value="• `! [pertanyaan]`: Mengajukan pertanyaan ke AI.\n*(Contoh: `!siapa penemu listrik`)*\n\n**Status:** ✅ **(Online)**", inline=False)
    embed.set_footer(text="Bot HEYN4S v1.3")
    await ctx.reply(embed=embed)

# --- `on_message` DENGAN AI AKTIF ---
@bot.event
async def on_message(message):
    if message.author == bot.user or isinstance(message.channel, discord.DMChannel):
        return

    # 1. Jalankan dulu perintah kustom (!ping, !rules, !help)
    await bot.process_commands(message)

    # 2. Cek apakah ini pertanyaan untuk AI
    if message.content.startswith("!"):
        ctx = await bot.get_context(message)
        if ctx.command:
            return # Ini adalah !ping, !rules, atau !help. Berhenti di sini.

        pertanyaan = message.content[1:].strip()
        if not pertanyaan:
            return

        async with message.channel.typing():
            jawaban_ai = None
            sumber_ai = "Tidak diketahui"
            error_log = {}

            # --- LOGIKA FALLBACK AI ---
            
            # 1. Coba Groq (Prioritas Utama)
            if groq_client:
                try:
                    print(f"Mencoba Groq untuk: {pertanyaan}")
                    response = groq_client.chat.completions.create(
                        # ⬇️ MODEL BARU YANG STABIL ⬇️
                        model="llama3-70b-8192", 
                        messages=[{"role": "user", "content": pertanyaan}]
                    )
                    if response.choices and response.choices[0].message.content:
                        jawaban_ai = response.choices[0].message.content
                        sumber_ai = "Groq (Llama 3)"
                except Exception as e_groq:
                    print(f"ERROR Groq Gagal: {e_groq}")
                    error_log['Groq'] = str(e_groq)

            # 2. Jika Groq Gagal, Coba Gemini
            if jawaban_ai is None and gemini_model:
                try:
                    print(f"Groq gagal, mencoba fallback Gemini...")
                    response = await gemini_model.generate_content_async(pertanyaan)
                    if response.parts:
                        jawaban_ai = response.text
                        sumber_ai = "Gemini"
                except Exception as e_gemini:
                    print(f"ERROR Gemini Gagal: {e_gemini}")
                    error_log['Gemini'] = str(e_gemini)

            # 3. Jika Gemini Gagal, Coba OpenAI
            if jawaban_ai is None and openai_client:
                try:
                    print(f"Gemini gagal, mencoba fallback OpenAI...")
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": pertanyaan}]
                    )
                    if response.choices and response.choices[0].message.content:
                        jawaban_ai = response.choices[0].message.content
                        sumber_ai = "ChatGPT"
                except Exception as e_openai:
                    print(f"ERROR OpenAI Gagal: {e_openai}")
                    error_log['OpenAI'] = str(e_openai)

            # 4. Jika Semua Gagal
            if jawaban_ai is None or jawaban_ai.isspace():
                jawaban_ai = f"Maaf, semua layanan AI sedang bermasalah.\n`Error Groq: {error_log.get('Groq', 'N/A')}`\n`Error Gemini: {error_log.get('Gemini', 'N/A')}`\n`Error OpenAI: {error_log.get('OpenAI', 'N/A')}`"
                sumber_ai = "Sistem"
            # --- Akhir Logika ---

            # Kirim Jawaban
            try:
                embed = discord.Embed(title="🤔 Pertanyaan Anda:", description=f"```{pertanyaan}```", color=discord.Color.blue())
                embed.add_field(name=f"🤖 Jawaban dari {sumber_ai}:", value=jawaban_ai[:4000], inline=False)
                embed.set_footer(text=f"Dijawab untuk: {message.author.display_name}")
                await message.reply(embed=embed)
            except discord.errors.Forbidden:
                await message.reply(f"**Jawaban dari {sumber_ai}:**\n{jawaban_ai[:1900]}")
            except Exception as e_send:
                print(f"Error mengirim pesan Discord: {e_send}")

# --- Menjalankan Bot DAN Web Server ---
if TOKEN:
    start_keep_alive()
    bot.run(TOKEN)
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")