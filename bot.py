import os
import discord
import openai  # <-- Kita pakai ini untuk MaiaRouter
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

# --- Konfigurasi AI (MAIAROUTER) ---
try:
    # API Key bisa diisi apa saja, 'sk-' sudah cukup
    # 'base_url' adalah bagian yang paling penting
    MAIA_API_KEY = "sk-maia-free-for-all" 
    MAIA_BASE_URL = "https://maia.router.litellm.ai" # Endpoint MaiaRouter

    maia_client = openai.OpenAI(
        api_key=MAIA_API_KEY,
        base_url=MAIA_BASE_URL
    )
    print("Model AI (MaiaRouter) berhasil dikonfigurasi.")
except Exception as e:
    print(f"ERROR: Gagal mengkonfigurasi MaiaRouter: {e}")
    maia_client = None
# --- Akhir Konfigurasi ---


# --- Inisialisasi Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
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

@bot.event
async def on_member_leave(member):
    guild = member.guild
    member_count = guild.member_count
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} member di HEYN4S")
    await bot.change_presence(status=discord.Status.online, activity=activity)

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
    embed.add_field(name="Perintah AI", value="• `! [pertanyaan]`: Mengajukan pertanyaan ke AI.\n*(Contoh: `!siapa penemu listrik`)*\n\n**Status:** ✅ **(Online - Powered by MaiaRouter)**", inline=False)
    embed.set_footer(text="Bot HEYN4S v1.7 - Powered by MaiaRouter")
    await ctx.reply(embed=embed)

# --- `on_message` DENGAN FOKUS HANYA PADA MAIAROUTER ---
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
            sumber_ai = "MaiaRouter"

            # --- HANYA MENCOBA MAIAROUTER ---
            if maia_client:
                try:
                    print(f"Mencoba MaiaRouter untuk: {pertanyaan}")
                    
                    # Kita harus menjalankan ini di 'executor' agar tidak memblokir bot
                    # karena library 'openai' tidak 'async'
                    response = await bot.loop.run_in_executor(
                        None, 
                        lambda: maia_client.chat.completions.create(
                            model="gpt-3.5-turbo", # MaiaRouter akan meneruskannya
                            messages=[{"role": "user", "content": pertanyaan}]
                        )
                    )

                    if response.choices and response.choices[0].message.content:
                        jawaban_ai = response.choices[0].message.content
                    else:
                        jawaban_ai = "Maaf, MaiaRouter merespons dengan jawaban kosong."

                except Exception as e_maia:
                    print(f"ERROR MaiaRouter Gagal: {e_maia}")
                    jawaban_ai = f"Maaf, layanan AI (MaiaRouter) gagal merespons.\n`Error: {e_maia}`"
            else:
                jawaban_ai = "Maaf, layanan AI (MaiaRouter) tidak dikonfigurasi."
            
            # --- AKHIR LOGIKA ---

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