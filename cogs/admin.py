import discord
from discord.ext import commands
async def is_guild_owner(ctx):
    return ctx.author.id == ctx.guild.owner_id

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Perintah 1: Refresh Member Count ---
    @commands.command(name="refresh")
    @commands.check(is_guild_owner) 
    async def refresh_presence(self, ctx):
        """(Owner) Me-refresh status hitungan member."""
        print("Mencoba refresh member count (diminta by owner)...")
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
            # --- AKHIR PERUBAHAN ---

        except Exception as e:
            await ctx.reply(f"Gagal refresh: {e}")

    # --- Error Handler untuk Perintah Admin ---
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.cog is not self:
            return 
            
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("Maaf, perintah ini hanya untuk Owner Server.", delete_after=10)
            await ctx.message.delete(delay=10)


def setup(bot):
    bot.add_cog(Admin(bot))