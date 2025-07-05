import os
import discord
import requests
from dotenv import load_dotenv
from discord.ext import tasks # -> [BARU] Impor modul untuk tugas berulang

# Muat environment variables dari file .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# -> [BARU] Konfigurasi untuk notifikasi otomatis
CHANNEL_ID_PENGUMUMAN = 1391188613793972254 # <<< GANTI DENGAN ID CHANNEL ANDA
MAGNITUDE_THRESHOLD = 5.0 # Ambang batas magnitudo untuk notifikasi
last_earthquake_time = "" # Variabel untuk menyimpan waktu gempa terakhir

CHANNEL_ID_BERITA = 1391188613793972254
# Inisialisasi bot
bot = discord.Bot()

# -> [BARU & DIPERBARUI] Event saat bot siap dan online
@bot.event
async def on_ready():
    """Fungsi yang dipanggil ketika bot berhasil terhubung ke Discord."""
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')
    
    activity = discord.Activity(type=discord.ActivityType.watching, name="server HEYN4S")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Status bot berhasil diubah!")

    # Memulai semua loop otomatis
    check_for_earthquakes.start()
    post_latest_news.start() # -> [BARU] Memulai loop pengecekan berita
    print("Semua loop otomatis telah dimulai.")


# Loop untuk kirim info gempa tiap 5 menit
@tasks.loop(minutes=5)
async def check_for_earthquakes():
    global last_earthquake_time
    # ... (kode loop gempa dari sebelumnya, tidak perlu diubah) ...
    # ... (untuk keringkasan, kode ini tidak ditampilkan ulang di sini) ...
    # Pastikan kode loop gempa Anda yang sebelumnya ada di sini
    url = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        gempa_terbaru = data['Infogempa']['gempa']
        waktu_gempa_sekarang = gempa_terbaru['Jam']
        magnitude_sekarang = float(gempa_terbaru['Magnitude'])
        if waktu_gempa_sekarang != last_earthquake_time and magnitude_sekarang >= MAGNITUDE_THRESHOLD:
            channel = bot.get_channel(CHANNEL_ID_GEMPA)
            if channel:
                embed = discord.Embed(
                    title=f"🚨 PERINGATAN: Gempa Kuat Terdeteksi!",
                    description=f"**Lokasi: {gempa_terbaru['Wilayah']}**",
                    color=discord.Color.brand_red()
                )
                embed.add_field(name="Waktu", value=f"{gempa_terbaru['Tanggal']} {gempa_terbaru['Jam']}", inline=False)
                embed.add_field(name="Magnitudo", value=f"{gempa_terbaru['Magnitude']} SR", inline=True)
                embed.add_field(name="Kedalaman", value=gempa_terbaru['Kedalaman'], inline=True)
                embed.add_field(name="Potensi", value=gempa_terbaru['Potensi'], inline=False)
                embed.set_footer(text="Data disediakan oleh BMKG | Bot untuk HEYN4S")
                await channel.send(embed=embed)
                last_earthquake_time = waktu_gempa_sekarang
    except Exception as e:
        print(f"Terjadi error saat loop pengecekan gempa: {e}")

# -> [BARU] Loop untuk memposting berita setiap 3 jam
@tasks.loop(hours=3)
async def post_latest_news():
    """Mengecek API berita dan mengirim 5 berita teratas ke channel."""
    print("Memeriksa berita terkini...")
    if not NEWS_API_KEY:
        print("Error: News API Key tidak diatur untuk loop berita.")
        return

    channel = bot.get_channel(CHANNEL_ID_BERITA)
    if not channel:
        print(f"Error: Channel berita dengan ID {CHANNEL_ID_BERITA} tidak ditemukan.")
        return

    url = f"https://newsapi.org/v2/top-headlines?country=id&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'ok' and data['articles']:
            embed = discord.Embed(
                title="🇮🇩 5 Berita Terkini Indonesia",
                color=discord.Color.dark_blue()
            )
            description = ""
            for i, article in enumerate(data['articles'], 1):
                description += f"**{i}. [{article['title']}]({article['url']})**\n"
                description += f"*Sumber: {article['source']['name']}*\n\n"
            
            embed.description = description
            embed.set_footer(text="Didukung oleh NewsAPI.org | Update setiap 3 jam")
            
            await channel.send(embed=embed)
            print("Berita terkini berhasil diposting.")
        else:
            print("Gagal memproses data berita, status bukan 'ok' atau tidak ada artikel.")

    except Exception as e:
        print(f"Terjadi error saat loop pengecekan berita: {e}")


# Perintah Slash Command untuk info gempa (tidak berubah)
@bot.slash_command(name="gempa", description="Menampilkan info gempa terkini dari BMKG.")
async def gempa(ctx):
    url = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        gempa_terbaru = data['Infogempa']['gempa']
        embed = discord.Embed(
            title=f"Info Gempa Terkini: {gempa_terbaru['Wilayah']}",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/272/PNG/512/EQ_earthquake_3010.png")
        embed.add_field(name="Waktu", value=f"{gempa_terbaru['Tanggal']} {gempa_terbaru['Jam']}", inline=False)
        embed.add_field(name="Magnitudo", value=f"{gempa_terbaru['Magnitude']} SR", inline=True)
        embed.add_field(name="Kedalaman", value=gempa_terbaru['Kedalaman'], inline=True)
        embed.add_field(name="Koordinat", value=f"{gempa_terbaru['Lintang']} | {gempa_terbaru['Bujur']}", inline=False)
        embed.add_field(name="Potensi", value=gempa_terbaru['Potensi'], inline=False)
        embed.set_footer(text="Data disediakan oleh BMKG | Bot untuk HEYN4S")
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"Gagal mengambil data dari BMKG. Error: {e}")


# Perintah Slash Command untuk info cuaca (tidak berubah)
@bot.slash_command(name="cuaca", description="Menampilkan info cuaca di kota tertentu.")
async def cuaca(ctx, *, kota: str):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = { 'q': kota, 'appid': WEATHER_API_KEY, 'units': 'metric', 'lang': 'id' }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data['cod'] == 200:
            nama_kota = data['name']
            suhu = data['main']['temp']
            terasa_seperti = data['main']['feels_like']
            deskripsi = data['weather'][0]['description'].title()
            kelembapan = data['main']['humidity']
            icon_id = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
            embed = discord.Embed(
                title=f"Cuaca di {nama_kota}",
                description=f"**{deskripsi}**",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=icon_url)
            embed.add_field(name="Suhu", value=f"{suhu}°C", inline=True)
            embed.add_field(name="Terasa Seperti", value=f"{terasa_seperti}°C", inline=True)
            embed.add_field(name="Kelembapan", value=f"{kelembapan}%", inline=True)
            embed.set_footer(text="Data disediakan oleh OpenWeatherMap | Bot untuk HEYN4S")
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Tidak dapat menemukan cuaca untuk kota **{kota}**. Mohon periksa kembali nama kota.")
    except Exception as e:
        await ctx.respond(f"Gagal terhubung ke layanan cuaca. Error: {e}")



# Menjalankan bot dengan token
bot.run(TOKEN)