import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.reply(f"Pong! 🏓\nLatensi saya {latency_ms} ms.")

    @commands.command(name="rules")
    async def rules(self, ctx):
        embed = discord.Embed(title="📜 Peraturan Server HEYN4S", description="Berikut adalah peraturan yang wajib dipatuhi:", color=discord.Color.gold())
        embed.add_field(name="1. Jaga Bahasa", value="Dilarang berkata kasar, SARA, atau mem-bully member lain.", inline=False)
        embed.add_field(name="2. Dilarang Spam", value="Jangan mengirim spam, promosi, atau link aneh di luar channel yang disediakan.", inline=False)
        embed.add_field(name="3. No NSFW", value="Dilarang keras memposting konten 18+.", inline=False)
        embed.add_field(name="4. Gunakan Channel Semestinya", value="Post di channel yang sesuai dengan topiknya.", inline=False)
        embed.set_footer(text="Terima kasih atas kerja samanya!")
        await ctx.reply(embed=embed)

    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(
            title="🤖 Bantuan Perintah Bot HEYN4S",
            description="Gunakan tanda seru `!` di depan perintah.\nContoh: `!ping`",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛠️ Perintah Utilitas", 
            value="• `!help`: Menampilkan pesan bantuan ini.\n"
                  "• `!avatar @user`: Lihat Foto Profil.\n"
                  "• `!userinfo @user`: Cek Info Akun.\n"
                  "• `!remind [menit] [pesan]`: Pasang Alarm.\n"
                  "• `!ping`: Cek kecepatan respons bot.\n"
                  "• `!rules`: Menampilkan peraturan server.\n"
                  "• `!poll [pertanyaan]`: Membuat voting Ya/Tidak.\n"
                  "• `!encode [teks]`: Mengubah teks ke Base64.\n"
                  "• `!decode [teks]`: Mengubah Base64 ke teks.",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Game",
            value="• `!math`: Game Matematika.\n"
                  "• `!jodoh @user`: Cek Jodoh.\n"
                  "• `!rate [hal]`: Rating.\n"
                  "• `!dadu`: Duel Dadu.\n"
                  "• `!suit`, `!slots`, `!koin`, `!bola8`",
            inline=False
        )

        embed.add_field(
            name="🔒 Perintah Admin",
            value="• `!refresh`: Memperbarui hitungan member di status bot.\n"
                  "• `!clear [jumlah]`: Menghapus pesan (contoh: `!clear 5`).\n"
                  "• `!say [channel] [pesan]`: Mengirim pengumuman (contoh: `!say #pengumuman halo semua`).",
            inline=False
        )
        
        embed.set_footer(text="Bot HEYN4S v2.3 - Stabil")
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))