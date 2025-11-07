import os
import discord
import google.generativeai as genai
import openai
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # <-- TAMBAHAN BARU

# --- Konfigurasi AI (Gemini) ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # PERBAIKAN: Mengganti ke 'gemini-pro' yang lebih stabil
    gemini_model = genai.GenerativeModel('gemini-pro') 
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI: {e}")
    gemini_model = None

# --- Konfigurasi AI (OpenAI / ChatGPT) ---
try:
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        print("Model AI (OpenAI) berhasil dikonfigurasi.")
    else:
        print("PERINGATAN: OPENAI_API_KEY tidak diatur. Fallback ChatGPT dinonaktifkan.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi OpenAI: {e}")
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
    if gemini_model:
        print("Bot AI (Gemini) siap digunakan.")
    if OPENAI_API_KEY:
        print("Bot AI (OpenAI Fallback) siap digunakan.")

# --- LOGIKA BARU: Menangani Pesan (Prefix '!') ---
@bot.event
async def on_message(message):
    if message.author == bot.user or isinstance(message.channel, discord.DMChannel):
        return

    if message.content.startswith("!"):
        pertanyaan = message.content[1:].strip()
        if not pertanyaan:
            return

        # Tampilkan "Bot is typing..."
        async with message.channel.typing():
            jawaban_ai = None
            sumber_ai = "Tidak diketahui"

            # --- LOGIKA FALLBACK BARU ---
            
            # 1. Coba Gemini Terlebih Dahulu
            if gemini_model:
                try:
                    print(f"Mencoba Gemini untuk: {pertanyaan}")
                    response = await gemini_model.generate_content_async(pertanyaan)
                    jawaban_ai = response.text
                    sumber_ai = "Gemini"
                except Exception as e_gemini:
                    print(f"ERROR Gemini Gagal: {e_gemini}")
                    jawaban_ai = None # Pastikan jawaban kosong agar fallback terpicu

            # 2. Jika Gemini Gagal (atau tidak ada), Coba OpenAI
            if jawaban_ai is None and OPENAI_API_KEY:
                try:
                    print(f"Gemini gagal, mencoba fallback OpenAI...")
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo", # Model ChatGPT yang cepat & murah
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": pertanyaan}
                        ]
                    )
                    jawaban_ai = response.choices[0].message.content
                    sumber_ai = "ChatGPT"
                except Exception as e_openai:
                    print(f"ERROR OpenAI Gagal: {e_openai}")
                    jawaban_ai = f"Maaf, kedua AI (Gemini dan ChatGPT) sedang bermasalah.\n`Gemini Error: {e_gemini}`\n`ChatGPT Error: {e_openai}`"

            # 3. Jika Keduanya Tidak Dikonfigurasi
            if jawaban_ai is None:
                jawaban_ai = "Maaf, tidak ada layanan AI yang dikonfigurasi. Hubungi admin."

            # --- Akhir Logika Fallback ---

            # Kirim Jawaban
            try:
                embed = discord.Embed(
                    title="🤔 Pertanyaan Anda:",
                    description=f"```{pertanyaan}```",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name=f"🤖 Jawaban dari {sumber_ai}:",
                    value=jawaban_ai[:4000], # Batasi jawaban
                    inline=False
                )
                embed.set_footer(text=f"Dijawab untuk: {message.author.display_name}")
                await message.reply(embed=embed)
            except Exception as e_send:
                print(f"Error mengirim pesan Discord: {e_send}")
                await message.reply("Maaf, terjadi kesalahan saat menampilkan jawaban.")
                
    await bot.process_commands(message)

# --- Menjalankan Bot DAN Web Server ---
if TOKEN:
    start_keep_alive()
    bot.run(TOKEN)
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di Secrets.")