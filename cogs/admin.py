import discord
from discord.ext import commands

# ----------------------------------------------------
# GANTI NAMA ROLE ADMIN ANDA DI SINI
NAMA_ROLE_ADMIN = "CEO" 
# ----------------------------------------------------


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Perintah 1: Refresh Member Count ---
    
    @commands.command(name="refresh")
    @commands.has_role(NAMA_ROLE_ADMIN)
    async def refresh_presence(self, ctx):
        """(Admin) Me-refresh status hitungan member."""
        print("Mencoba refresh member count (diminta by admin)...")
        try:
            guild = ctx.guild
            member_count = guild.member_count
            activity = discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"{member_count} member di HEYN4S"
            )
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            
            await ctx.reply("✅ Status *member count* berhasil di-refresh!", delete_after=10)
            await ctx.message.delete(delay=10)

        except Exception as e:
            await ctx.reply(f"Gagal refresh: {e}")

    # --- FITUR BARU 1: Clear Messages ---

    @commands.command(name="clear")
    @commands.has_role(NAMA_ROLE_ADMIN)
    async def clear_messages(self, ctx, amount: int):
        """(Admin) Menghapus beberapa pesan terakhir."""
        if amount <= 0:
            await ctx.reply("Jumlah harus lebih dari 0.", delete_after=10)
            await ctx.message.delete(delay=10)
            return
        
        await ctx.message.delete() # Hapus perintah `!clear` itu sendiri
        deleted_messages = await ctx.channel.purge(limit=amount)
        await ctx.send(f"✅ Berhasil menghapus {len(deleted_messages)} pesan.", delete_after=5)

    # --- FITUR BARU 2: Say (Pengumuman) ---
    
    @commands.command(name="say")
    @commands.has_role(NAMA_ROLE_ADMIN)
    async def say_message(self, ctx, channel: discord.TextChannel, *, message: str):
        """(Admin) Mengirim pesan embed sebagai bot."""
        
        # Buat embed yang rapi
        embed = discord.Embed(
            description=message,
            color=discord.Color.blue()
        )
        embed.set_author(
            name=f"Pengumuman dari {ctx.author.display_name}", 
            icon_url=ctx.author.avatar.url
        )
        
        try:
            await channel.send(embed=embed)
            # Beri tahu owner bahwa perintah berhasil
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.reply(f"Gagal mengirim pesan: {e}")

    # --- Error Handler Canggih untuk SEMUA Perintah Admin ---
    
    async def cog_command_error(self, ctx, error):
        """Menangkap error HANYA untuk perintah di cog Admin ini."""
        
        if isinstance(error, commands.MissingRole):
            # Jika user tidak punya role "CEO"
            await ctx.reply(f"Maaf, perintah ini hanya untuk member dengan role `{NAMA_ROLE_ADMIN}`.", delete_after=10)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            # Jika perintah kurang argumen (misal: `!clear` tapi tanpa jumlah)
            await ctx.reply(f"Perintah Anda kurang lengkap. Cek `!help` untuk contoh.", delete_after=10)
        
        elif isinstance(error, commands.BadArgument):
            # Jika argumen salah (misal: `!clear halo` atau `!say #channel-ngawur`)
            await ctx.reply(f"Argumen yang Anda berikan salah. Cek `!help`.", delete_after=10)
        
        else:
            # Error lainnya
            await ctx.reply(f"Terjadi error: {error}", delete_after=10)
            print(f"Error di cog Admin: {error}") # Log ke konsol

        # Hapus pesan perintah yang salah
        try:
            await ctx.message.delete(delay=10)
        except Exception:
            pass # Abaikan jika pesan sudah terhapus

def setup(bot):
    bot.add_cog(Admin(bot))