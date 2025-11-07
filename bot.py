import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask         # <-- TAMBAHAN BARU
from threading import Thread    # <-- TAMBAHAN BARU

# --- Konfigurasi Web Server (Agar Bot Tetap Online) ---
# Ini adalah "situs web" palsu yang dibutuhkan Koyeb
app = Flask('')

@app.route('/')
def home():
    return "Bot AI sedang aktif."

def run_server():
    # Mengambil Port dari Koyeb secara otomatis
    port = int(os.environ.get('PORT', 8080)) 
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    """Menjalankan web server di thread terpisah."""
    t = Thread(target=run_server)
    t.start()
# --- AKHIR BAGIAN BARU ---


# --- Muat Konfigurasi Bot ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- Konfigurasi AI (Gemini) ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI. Periksa GEMINI_API_KEY Anda.")
    model = None

# --- Inisialisasi Bot ---
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    """Dipanggil ketika bot berhasil terhubung ke Discord."""
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    activity = discord.Activity(type=discord.ActivityType.listening, name="pertanyaan di HEYN4S")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    if model:
        print("Bot AI tanya-jawab siap digunakan.")
    else:
        print("PERINGATAN: Bot online, tapi fitur AI tidak aktif.")

# --- Perintah Slash Command AI ---
@bot.slash_command(
    name="tanya",
    description="Ajukan pertanyaan apapun kepada AI."
)
async def tanya(
    ctx,
    pertanyaan: discord.Option(str, "Tulis pertanyaanmu di sini.", required=True)
):
    if not model:
        await ctx.respond(
            "Maaf, layanan AI sedang tidak terkonfigurasi. Silakan hubungi admin bot.",
            ephemeral=True
        )
        return
    
    await ctx.defer()

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
        embed.set_footer(text=f"Dijawab untuk: {ctx.author.display_name}")
        await ctx.followup.send(embed=embed)

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        await ctx.followup.send(
            f"Maaf, terjadi kesalahan saat memproses pertanyaanmu.\n`Error: {e}`",
            ephemeral=True
        )

# --- Menjalankan Bot DAN Web Server ---
if TOKEN:
    start_keep_alive()  # <-- INI MENJALANKAN SERVER WEB
    bot.run(TOKEN)      # <-- INI MENJALANKAN BOT ANDA
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di file .env atau Secrets.")