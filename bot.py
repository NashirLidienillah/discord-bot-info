import os
import discord
import google.generativeai as genai
import openai
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 

try:
    genai.configure(api_key=GEMINI_API_KEY)
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

        async with message.channel.typing():
            jawaban_ai = None
            sumber_ai = "Tidak diketahui"
            error_gemini_msg = "" # Untuk menyimpan error

            # 1. Coba Gemini Terlebih Dahulu
            if gemini_model:
                try:
                    print(f"Mencoba Gemini untuk: {pertanyaan}")
                    response = await gemini_model.generate_content_async(pertanyaan)
                    
                    # --- PENGECEKAN BARU (ANTI-CRASH) ---
                    # Cek jika respons diblokir atau kosong
                    if response.parts:
                        jawaban_ai = response.text
                    else:
                        jawaban_ai = None # Paksa fallback jika respons kosong
                        print("Peringatan: Respons Gemini kosong (mungkin difilter).")
                    # --- AKHIR PENGECEKAN ---

                    sumber_ai = "Gemini"
                except Exception as e_gemini:
                    print(f"ERROR Gemini Gagal: {e_gemini}")
                    error_gemini_msg = str(e_gemini) # Simpan pesan error
                    jawaban_ai = None 

            # 2. Jika Gemini Gagal (jawaban_ai masih None), Coba OpenAI
            if jawaban_ai is None and OPENAI_API_KEY:
                try:
                    print(f"Gemini gagal, mencoba fallback OpenAI...")
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": pertanyaan}
                        ]
                    )
                    
                    # --- PENGECEKAN BARU (ANTI-CRASH) ---
                    if response.choices and response.choices[0].message.content:
                        jawaban_ai = response.choices[0].message.content
                    else:
                        jawaban_ai = None # Respons OpenAI juga kosong
                        print("Peringatan: Respons OpenAI kosong (mungkin difilter).")
                    # --- AKHIR PENGECEKAN ---

                    sumber_ai = "ChatGPT"
                except Exception as e_openai:
                    print(f"ERROR OpenAI Gagal: {e_openai}")
                    jawaban_ai = f"Maaf, kedua AI (Gemini dan ChatGPT) sedang bermasalah.\n`Gemini Error: {error_gemini_msg}`\n`ChatGPT Error: {e_openai}`"

            # 3. Jika Keduanya Gagal atau Respons Kosong
            if jawaban_ai is None or jawaban_ai.isspace():
                jawaban_ai = "Maaf, AI tidak memberikan respons yang valid. Ini mungkin karena filter keamanan atau pertanyaan yang terlalu singkat."

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
                    value=jawaban_ai[:4000], 
                    inline=False
                )
                embed.set_footer(text=f"Dijawab untuk: {message.author.display_name}")
                await message.reply(embed=embed)
            
            # Ini akan menangkap error "Missing Permissions" (Embed Links)
            except discord.errors.Forbidden:
                print("ERROR: Bot tidak punya izin 'Embed Links'. Mengirim sebagai teks biasa.")
                await message.reply(f"**Jawaban dari {sumber_ai}:**\n{jawaban_ai[:1900]}")
            
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