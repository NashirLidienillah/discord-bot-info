import os
import discord
import google.generativeai as genai
import openai
import groq  # <-- IMPORT BARU
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
# --- Akhir Web Server ---

# --- Muat Konfigurasi Bot ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY') # <-- KEY BARU

# --- Konfigurasi AI (Gemini) ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.0-pro') # Model stabil
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI: {e}")
    gemini_model = None

# --- Konfigurasi AI (OpenAI) ---
try:
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("Model AI (OpenAI) berhasil dikonfigurasi.")
    else:
        openai_client = None
        print("PERINGATAN: OPENAI_API_KEY tidak diatur.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi OpenAI: {e}")
    openai_client = None

# --- Konfigurasi AI (Groq) ---
try:
    if GROQ_API_KEY:
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
        print("Model AI (Groq) berhasil dikonfigurasi.")
    else:
        groq_client = None
        print("PERINGATAN: GROQ_API_KEY tidak diatur.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Groq: {e}")
    groq_client = None
# --- Akhir Konfigurasi ---


# --- Inisialisasi Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    activity = discord.Activity(type=discord.ActivityType.listening, name="perintah !")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    if groq_client: print("Bot AI (Groq) siap digunakan.")
    if gemini_model: print("Bot AI (Gemini Fallback) siap digunakan.")
    if openai_client: print("Bot AI (OpenAI Fallback) siap digunakan.")

# --- LOGIKA BARU: Menangani Pesan (Prefix '!') ---
@bot.event
async def on_message(message):
    if message.author == bot.user or isinstance(message.channel, discord.DMChannel):
        return

    if message.content.startswith("!"):
        pertanyaan = message.content[1:].strip()
        if not pertanyaan:
            return

        async with message.channel.typing():
            jawaban_ai = None
            sumber_ai = "Tidak diketahui"
            error_log = {} # Untuk menyimpan semua error

            # --- LOGIKA PRIORITAS AI ---
            
            # 1. Prioritas 1: Coba Groq (Cepat & Gratis)
            if groq_client:
                try:
                    print(f"Mencoba Groq untuk: {pertanyaan}")
                    response = groq_client.chat.completions.create(
                        model="llama3-8b-8192", # Model Llama 3 yang cepat
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
                    else:
                        print("Peringatan: Respons Gemini kosong (filter).")
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
                jawaban_ai = f"Maaf, semua layanan AI sedang bermasalah atau tidak dikonfigurasi.\n`Error Groq: {error_log.get('Groq', 'N/A')}`\n`Error Gemini: {error_log.get('Gemini', 'N/A')}`\n`Error OpenAI: {error_log.get('OpenAI', 'N/A')}`"
                sumber_ai = "Sistem"
            # --- Akhir Logika ---

            # Kirim Jawaban
            try:
                embed = discord.Embed(
                    title="🤔 Pertanyaan Anda:",
                    description=f"```{pertanyaan}```",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name=f"🤖 Jawaban dari {sumber_ai}:",
                    value=jawaban_ai[:4000],
                    inline=False
                )
                embed.set_footer(text=f"Dijawab untuk: {message.author.display_name}")
                await message.reply(embed=embed)
            
            except discord.errors.Forbidden:
                print("ERROR: Bot tidak punya izin 'Embed Links'. Mengirim sebagai teks biasa.")
                await message.reply(f"**Jawaban dari {sumber_ai}:**\n{jawaban_ai[:1900]}")
            except Exception as e_send:
                print(f"Error mengirim pesan Discord: {e_send}")

    await bot.process_commands(message)

# --- Menjalankan Bot DAN Web Server ---
if TOKEN:
    start_keep_alive()
    bot.run(TOKEN)
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")