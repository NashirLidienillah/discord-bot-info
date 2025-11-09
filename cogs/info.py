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
        
        # --- PERUBAHAN DI SINI ---
        embed.add_field(
            name="🔒 Perintah Admin",
            value="• `!refresh`: Memperbarui hitungan member di status bot.\n"
                  "• `!clear [jumlah]`: Menghapus pesan (contoh: `!clear 5`).\n"
                  "• `!say [channel] [pesan]`: Mengirim pengumuman (contoh: `!say #pengumuman halo semua`).",
            inline=False
        )
        # --- AKHIR PERUBAHAN ---
        
        embed.set_footer(text="Bot HEYN4S v2.2 - Stabil")
        await ctx.reply(embed=embed)