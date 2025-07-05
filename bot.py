import os
import discord
import requests
from dotenv import load_dotenv

# Muat environment variables dari file .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Inisialisasi bot
bot = discord.Bot()

@bot.event
async def on_ready():
    """Fungsi yang dipanggil ketika bot berhasil terhubung ke Discord."""
    print(f'Bot telah login sebagai {bot.user}')
    print('-----------------------------------------')

# Perintah Slash Command untuk info gempa
@bot.slash_command(name="gempa", description="Menampilkan info gempa terkini dari BMKG.")
async def gempa(ctx):
    """Mengambil dan menampilkan data gempa terkini dari API BMKG."""
    # URL API BMKG
    url = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
    try:
        # Mengirim request ke API
        response = requests.get(url)
        response.raise_for_status() # Akan error jika status code bukan 2xx
        data = response.json()
        
        # Mengambil data gempa terbaru
        gempa_terbaru = data['Infogempa']['gempa']
        
        # Membuat embed message agar tampilan lebih rapi
        embed = discord.Embed(
            title=f"🚨 Gempa Terkini: {gempa_terbaru['Wilayah']}",
            color=discord.Color.red() # Warna merah untuk penanda bahaya
        )
        embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/272/PNG/512/EQ_earthquake_3010.png")
        embed.add_field(name="Waktu", value=f"{gempa_terbaru['Tanggal']} {gempa_terbaru['Jam']}", inline=False)
        embed.add_field(name="Magnitudo", value=f"{gempa_terbaru['Magnitude']} SR", inline=True)
        embed.add_field(name="Kedalaman", value=gempa_terbaru['Kedalaman'], inline=True)
        embed.add_field(name="Koordinat", value=f"{gempa_terbaru['Lintang']} | {gempa_terbaru['Bujur']}", inline=False)
        embed.add_field(name="Potensi", value=gempa_terbaru['Potensi'], inline=False)
        embed.set_footer(text="Data disediakan oleh BMKG")

        await ctx.respond(embed=embed)
        
    except requests.exceptions.RequestException as e:
        await ctx.respond(f"Gagal mengambil data dari BMKG. Error: {e}")
    except KeyError:
        await ctx.respond("Format data dari BMKG berubah. Gagal memparsing data.")


# Perintah Slash Command untuk info cuaca
@bot.slash_command(name="cuaca", description="Menampilkan info cuaca di kota tertentu.")
async def cuaca(ctx, *, kota: str):
    """Mengambil dan menampilkan data cuaca dari OpenWeatherMap."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': kota,
        'appid': WEATHER_API_KEY,
        'units': 'metric', # Untuk satuan Celcius
        'lang': 'id'      # Untuk deskripsi dalam Bahasa Indonesia
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data['cod'] == 200:
            # Mengambil data yang relevan
            nama_kota = data['name']
            suhu = data['main']['temp']
            terasa_seperti = data['main']['feels_like']
            deskripsi = data['weather'][0]['description'].title()
            kelembapan = data['main']['humidity']
            icon_id = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"

            # Membuat embed message
            embed = discord.Embed(
                title=f"Cuaca di {nama_kota}",
                description=f"**{deskripsi}**",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=icon_url)
            embed.add_field(name="Suhu", value=f"{suhu}°C", inline=True)
            embed.add_field(name="Terasa Seperti", value=f"{terasa_seperti}°C", inline=True)
            embed.add_field(name="Kelembapan", value=f"{kelembapan}%", inline=True)
            embed.set_footer(text="Data disediakan oleh OpenWeatherMap")
            
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Tidak dapat menemukan cuaca untuk kota **{kota}**. Mohon periksa kembali nama kota.")
            
    except requests.exceptions.RequestException as e:
        await ctx.respond(f"Gagal terhubung ke layanan cuaca. Error: {e}")

# Menjalankan bot dengan token
bot.run(TOKEN)