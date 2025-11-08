import discord
from discord.ext import commands
import base64

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Fitur 1: Kriptografi ---
    
    @commands.command(name="encode")
    async def encode_base64(self, ctx, *, text_to_encode: str):
        """Meng-encode teks ke Base64."""
        try:
            encoded_bytes = base64.b64encode(text_to_encode.encode('utf-8'))
            encoded_string = encoded_bytes.decode('utf-8')
            
            embed = discord.Embed(title="🔐 Base64 Encoder", color=discord.Color.blue())
            embed.add_field(name="Teks Asli", value=f"```\n{text_to_encode}\n```", inline=False)
            embed.add_field(name="Hasil Encode", value=f"```\n{encoded_string}\n```", inline=False)
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"Terjadi error saat encode: {e}")

    @commands.command(name="decode")
    async def decode_base64(self, ctx, *, encoded_text: str):
        """Me-decode teks dari Base64."""
        try:
            decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
            decoded_string = decoded_bytes.decode('utf-8')
            
            embed = discord.Embed(title="🔓 Base64 Decoder", color=discord.Color.green())
            embed.add_field(name="Teks Base64", value=f"```\n{encoded_text}\n```", inline=False)
            embed.add_field(name="Hasil Decode", value=f"```\n{decoded_string}\n```", inline=False)
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"Gagal decode. Pastikan teks adalah Base64 yang valid. Error: {e}")

    # --- Fitur 2: Polling ---

    @commands.command(name="poll")
    async def poll(self, ctx, *, question: str):
        """Membuat jajak pendapat (voting) Ya/Tidak."""
        embed = discord.Embed(
            title="📊 Jajak Pendapat Baru",
            description=f"**{question}**",
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Dimulai oleh: {ctx.author.display_name}")
        
        # Kirim pesan poll dan simpan
        poll_message = await ctx.send(embed=embed)
        
        # Tambahkan reaksi
        await poll_message.add_reaction("🇾") # Ya
        await poll_message.add_reaction("🇳") # Tidak
        
        # Hapus pesan perintah asli
        try:
            await ctx.message.delete()
        except Exception as e:
            print(f"Gagal hapus pesan poll: {e}")


def setup(bot):
    bot.add_cog(Utility(bot))