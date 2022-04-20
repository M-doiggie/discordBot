import random

from discord.ext import commands
from mcstatus import MinecraftServer


class MiscCommands(commands.Cog):

    # Pings a minecraft server and tells you if it is up and how many people are online
    @commands.command(name="status", help="Tells you the status of the minecraft server...if it is still alive")
    async def sendMCServerStatus(self, ctx):
        await ctx.channel.send("This might take a minute.")
        server = MinecraftServer.lookup("gallafent.duckdns.org")
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
