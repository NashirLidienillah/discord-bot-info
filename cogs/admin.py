import discord
from discord.ext import commands

NAMA_ROLE_ADMIN = "CEO" 

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @refresh_presence.error 
    async def refresh_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.reply(f"Maaf, perintah ini hanya untuk member dengan role `{NAMA_ROLE_ADMIN}`.", delete_after=10)
            await ctx.message.delete(delay=10)
        else:
            await ctx.reply(f"Terjadi error: {error}")


def setup(bot):
    bot.add_cog(Admin(bot))