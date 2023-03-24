from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer

import os
import youtube_dl
import discord


# cog de áudio experimental


class Audio:
    """comandos de áudio"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def local(self, ctx, *, filename: str):
        """tocar mp3"""

        if ctx.author.voice is None:
            await ctx.send("você precisa estar em um canal de voz...")
            return

        if ctx.guild.voice_client:
            if ctx.guild.voice_client.channel != ctx.author.voice.channel:
                await ctx.guild.voice_client.disconnect()

        path = os.path.join("cogs", "audio", "songs", filename + ".mp3")

        if not os.path.isfile(path):
            await ctx.send("nenhum arquivo foi encontrado para que seja tocado...")
            return
        
        player = PCMVolumeTransformer(FFmpegPCMAudio(path), volume=1)
        
        voice = await ctx.author.voice.channel.connect()
        voice.play(player)

        await ctx.send("{} está tocando uma música...".format(ctx.author))

    @commands.command()
    async def play(self, ctx, url: str):
        """tocar url do youtube"""

        url = url.strip("<").strip(">")

        if ctx.author.voice is None:
            await ctx.send("você precisa estar em um canal de voz...")
            return

        elif "youtube.com" not in url.lower():
            await ctx.send("o url do youtube especificado não é válido...")
            return

        if ctx.guild.voice_client:
            if ctx.guild.voice_client.channel != ctx.author.voice.channel:
                await ctx.guild.voice_client.disconnect()
                
        yt = YoutubeSource(url)

        player = PCMVolumeTransformer(yt, volume=1)

        voice = await ctx.author.voice.channel.connect()
        voice.play(player)

        await ctx.send("{} está tocando uma música...".format(ctx.author))

    @commands.command()
    async def stop(self, ctx):
        """para com a música e desconecta do canal de voz"""

        if ctx.guild.voice_client:
            ctx.guild.voice_client.source.cleanup()

            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("eu não estou conectado em nenhum canal de voz...", delete_after=2)

        await ctx.message.delete()

    @commands.command()
    async def pause(self, ctx):
        """pausa a música"""

        if ctx.guild.voice_client:
            ctx.guild.voice_client.pause()

            await ctx.send("música pausada com sucesso...", delete_after=2)
        else:
            await ctx.send("eu não estou conectado em nenhum canal de voz...", delete_after=2)

        await ctx.message.delete()

    @commands.command()
    async def resume(self, ctx):
        """volta a tocar a música"""

        if ctx.guild.voice_client:
            ctx.guild.voice_client.resume()

            await ctx.send("música retomada com sucesso...", delete_after=2)
        else:
            await ctx.send("eu não estou conectado em nenhum canal de voz...", delete_after=2)

        await ctx.message.delete()

    @commands.command(hidden=True)
    async def volume(self, ctx, n: float):
        """determina o volume das músicas"""

        if ctx.guild.voice_client:
            ctx.guild.voice_client.source.volume = n

            await ctx.send("volume determinado com sucesso...", delete_after=2)
        else:
            await ctx.send("eu não estou conectado em nenhum canal de voz...", delete_after=2)

        await ctx.message.delete()

    def __unload(self):
        for vc in self.bot.voice_client:
            if vc.source:
                vc.source.cleanup()

            self.bot.loop.create_task(vc.disconnect())

        
class YoutubeSource(discord.FFmpegPCMAudio):
    def __init__(self, url):
        opts = {
            'format': 'webm[abr>0]/bestaudio/best',
            'prefer_ffmpeg': True,
            'quiet': True
        }

        ytdl = youtube_dl.YoutubeDL(opts)

        self.info = ytdl.extract_info(url, download=False)

        super().__init__(self.info['url'])