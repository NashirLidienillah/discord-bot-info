from discord.ext import commands
import discord

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Cek latensi dan status bot."""
        latency_ms = round(self.bot.latency * 1000)
        await ctx.reply(f"Pong! 🏓\nLatensi saya {latency_ms} ms.")

    @commands.command(name="rules")
    async def rules(self, ctx):
        """Menampilkan peraturan server HEYN4S."""
        embed = discord.Embed(title="📜 Peraturan Server HEYN4S", description="Berikut adalah peraturan yang wajib dipatuhi:", color=discord.Color.gold())
        embed.add_field(name="1. Jaga Bahasa", value="Dilarang berkata kasar, SARA, atau mem-bully member lain.", inline=False)
        embed.add_field(name="2. Dilarang Spam", value="Jangan mengirim spam, promosi, atau link aneh di luar channel yang disediakan.", inline=False)
        embed.add_field(name="3. No NSFW", value="Dilarang keras memposting konten 18+.", inline=False)
        embed.add_field(name="4. Gunakan Channel Semestinya", value="Post di channel yang sesuai dengan topiknya.", inline=False)
        embed.set_footer(text="Terima kasih atas kerja samanya!")
        await ctx.reply(embed=embed)

    @commands.command(name="help")
    async def help(self, ctx):
        """Menampilkan daftar perintah bot."""
        embed = discord.Embed(
            title="🤖 Bantuan Perintah Bot HEYN4S",
            description="Gunakan tanda seru `!` di depan perintah.\nContoh: `!ping`",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Perintah Utilitas", 
            value="• `!help`: Menampilkan pesan bantuan ini.\n"
                  "• `!ping`: Cek kecepatan respons bot.\n"
                  "• `!rules`: Menampilkan peraturan server.\n"
                  "• `!poll [pertanyaan]`: Membuat voting Ya/Tidak.\n"
                  "• `!encode [teks]`: Mengubah teks ke Base64.\n"
                  "• `!decode [teks]`: Mengubah Base64 ke teks.",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Perintah Owner Server",
            value="• `!refresh`: Memperbarui hitungan member di status bot.",
            inline=False
        )
        embed.set_footer(text="Bot HEYN4S v2.1")
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))