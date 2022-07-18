import os
import random

import discord
from discord.ext import commands
from mcstatus import JavaServer

cum_img_url = "https://external-preview.redd.it/tXkvYCJzK9Gs9FXmNqFhCaUynmldrVdu2k_K0BpHv4I.jpg?auto=webp&s=907bbf6d1677a6e18c738e962998330fc36745ca"
SERVER_TOKEN = os.getenv("mc_server_token", "gallafent.duckdns.org")


class MiscCommands(commands.Cog):

    # Pings a minecraft server and tells you if it is up and how many people are online
    @commands.command(name="status", help="Tells you the status of the minecraft server...if it is still alive")
    async def sendMCServerStatus(self, ctx):
        await ctx.channel.send("This might take a minute.")
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
        embedMessage = discord.Embed(title="Silence Wench")
        embedMessage.description = "I do not wish to be horny anymore."
        embedMessage.set_image(url=cum_img_url)
        await ctx.channel.send(embed=embedMessage)
