import os
import random

import discord
from discord.ext import commands
from mcstatus import JavaServer

from Strings import Strings

SERVER_TOKEN = os.getenv("mc_server_token", "gallafent.duckdns.org")


class MiscCommands(commands.Cog):

    # Pings a minecraft server and tells you if it is up and how many people are online
    @commands.command(name="status", help="Tells you the status of the minecraft server...if it is still alive")
    async def sendMCServerStatus(self, ctx):
        await ctx.channel.send(Strings.slow_minecraft_returns.value)
        server = JavaServer.lookup(SERVER_TOKEN)
        status = server.status()

        await ctx.channel.send(f"The Minecraft server has {status.players.online} players on right now. "
                               f"\n Ping: {status.latency} " + "ms")

    # Tells the user the result of a coinflip
    @commands.command(name="coinflip", help="Flips a coin for you, heads or tails")
    async def flipACoin(self, ctx):
        if random.randint(0, 1) == 1:
            await ctx.channel.send("Heads!")
        else:
            await ctx.channel.send("Tails!")

    @commands.command(name="cum", help="Silence wench, I do not wish to be horny anymore")
    async def sendCum(self, ctx):
        embedMessage = discord.Embed(title=Strings.silence_wench_title)
        embedMessage.description = Strings.silence_wench_description.value
        embedMessage.set_image(url=Strings.cum_img_url.value)
        await ctx.channel.send(embed=embedMessage)

    @commands.command(name="flame", help="League of legends question mark ping")
    async def sendFlame(self, ctx):
        embedMessage = discord.Embed(title=Strings.flame_league_title)
        embedMessage.description = Strings.flame_league_description
        embedMessage.set_image(url=Strings.ping_gif_url.value)
        await ctx.channel.send(embed=embedMessage)
