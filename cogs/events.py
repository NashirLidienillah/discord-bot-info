from discord.ext import commands
import discord

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot telah login sebagai {self.bot.user}')
        print('-----------------------------------------')
        try:
            # Asumsi bot hanya ada di 1 server (HEYN4S)
            guild = self.bot.guilds[0]
            member_count = guild.member_count
            
            activity = discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"{member_count} member di HEYN4S"
            )
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            print(f"Status presence diupdate: {member_count} member.")
        
        except Exception as e:
            print(f"Gagal update presence saat on_ready: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Dipanggil saat ada member baru masuk."""
        guild = member.guild
        member_count = guild.member_count # Ambil jumlah member baru
        
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} member di HEYN4S"
        )
        await self.bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"Member baru bergabung, status diupdate: {member_count} member.")

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        """Dipanggil saat ada member keluar."""
        guild = member.guild
        member_count = guild.member_count # Ambil jumlah member baru
        
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} member di HEYN4S"
        )
        await self.bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"Member keluar, status diupdate: {member_count} member.")

def setup(bot):
    bot.add_cog(Events(bot))