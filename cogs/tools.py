import discord
from discord.ext import commands
import asyncio
from datetime import datetime

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- FITUR 1: Cek Avatar (Foto Profil) ---
    @commands.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx, member: discord.Member = None):
        """Melihat foto profil seseorang (HD)."""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"📸 Avatar {member.name}",
            color=discord.Color.teal()
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Direquest oleh: {ctx.author.name}")
        
        await ctx.reply(embed=embed)

    @commands.command(name="userinfo", aliases=["whois", "ui"])
    async def user_info(self, ctx, member: discord.Member = None):
        """Melihat informasi detail akun member."""
        member = member or ctx.author

        format_date = "%d/%m/%Y %H:%M"
        joined_at = member.joined_at.strftime(format_date)
        created_at = member.created_at.strftime(format_date)
        
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "Tidak ada role"

        embed = discord.Embed(title="👤 Informasi User", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="Nama Akun", value=f"{member.name}", inline=True)
        embed.add_field(name="Nickname Server", value=member.display_name, inline=True)
        embed.add_field(name="ID Akun", value=member.id, inline=False)
        embed.add_field(name="📅 Akun Dibuat", value=created_at, inline=True)
        embed.add_field(name="📥 Join Server", value=joined_at, inline=True)
        embed.add_field(name=f"🎭 Roles ({len(roles)})", value=roles_str, inline=False)
        
        await ctx.reply(embed=embed)

    # --- FITUR 3: Reminder (Alarm) ---
    @commands.command(name="remind", aliases=["timer"])
    async def reminder(self, ctx, waktu: int, *, pesan: str = "Waktu habis!"):
        """Pasang alarm (dalam menit). Contoh: !remind 10 Masak mie"""
        if waktu <= 0:
            await ctx.reply("Waktu harus lebih dari 0 menit!")
            return
            
        await ctx.reply(f"⏰ Oke! Saya akan mengingatkanmu tentang **'{pesan}'** dalam **{waktu} menit**.")
        await asyncio.sleep(waktu * 60)

        await ctx.send(f"🔔 {ctx.author.mention}, Waktunya: **{pesan}**!")

   
    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.reply("Waktu harus berupa angka (menit)! Contoh: `!remind 5 Mabar`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Format salah! Gunakan: `!remind [menit] [pesan]`")

def setup(bot):
    bot.add_cog(Tools(bot))