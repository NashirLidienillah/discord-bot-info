import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv

# --- Muat Konfigurasi ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- Konfigurasi AI (Gemini) ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Menggunakan model 'flash' yang cepat dan efisien
    model = genai.GenerativeModel('gemini-1.5-flash') 
    print("Model AI (Gemini) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi Gemini AI. Periksa GEMINI_API_KEY Anda.")
    print(f"Detail Error: {e}")
    model = None # Set model ke None agar bot tahu ada masalah

# --- Inisialisasi Bot ---
# Mengaktifkan 'intents' dasar agar bot bisa membaca pesan
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    """Dipanggil ketika bot berhasil terhubung ke Discord."""
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    
    # Mengubah status bot menjadi "Listening to pertanyaan"
    activity = discord.Activity(type=discord.ActivityType.listening, name="pertanyaan di HEYN4S")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    if model:
        print("Bot AI tanya-jawab siap digunakan.")
    else:
        print("PERINGATAN: Bot online, tapi fitur AI tidak aktif karena konfigurasi gagal.")

# --- Perintah Slash Command AI (Satu-satunya Fitur Baru) ---

@bot.slash_command(
    name="tanya", 
    description="Ajukan pertanyaan apapun kepada AI."
)
async def tanya(
    ctx, 
    pertanyaan: discord.Option(str, "Tulis pertanyaanmu di sini.", required=True)
):
    """Fungsi utama untuk merespons pertanyaan pengguna menggunakan AI."""
    
    # Cek jika model AI gagal dimuat saat startup
    if not model:
        await ctx.respond(
            "Maaf, layanan AI sedang tidak terkonfigurasi. Silakan hubungi admin bot.", 
            ephemeral=True
        )
        return

    # [PENTING] Memberi tahu Discord bahwa bot sedang "berpikir"
    # Ini mencegah error timeout jika AI butuh waktu lama untuk menjawab
    await ctx.defer()

    try:
        # Mengirim pertanyaan ke API Gemini
        response = await model.generate_content_async(pertanyaan)
        
        # Membuat Embed (tampilan) untuk jawaban
        embed = discord.Embed(
            title="🤔 Pertanyaan Anda:",
            description=f"```{pertanyaan}```",
            color=discord.Color.blue()
        )
        
        # Menambahkan jawaban AI ke embed
        # Kita batasi 4000 karakter untuk keamanan (batas Discord)
        jawaban_ai = response.text[:4000] 
        
        embed.add_field(
            name="🤖 Jawaban AI:",
            value=jawaban_ai,
            inline=False
        )
        embed.set_footer(text=f"Dijawab untuk: {ctx.author.display_name}")

        # Mengirim jawaban (menggunakan followup karena kita sudah pakai defer)
        await ctx.followup.send(embed=embed)

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        await ctx.followup.send(
            f"Maaf, terjadi kesalahan saat memproses pertanyaanmu.\n`Error: {e}`", 
            ephemeral=True
        )

# --- Menjalankan Bot ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("FATAL ERROR: DISCORD_TOKEN tidak ditemukan di file .env. Bot tidak bisa dijalankan.")