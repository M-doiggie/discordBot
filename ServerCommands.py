from discord.ext import commands
import docker


class ServerCommands(commands.Cog):

    @commands.command(name='activate', help='Starts up the listed server')
    async def startup(self, ctx, *, url):
        # Ping the mc server to start up
        return

    @commands.command(name='servers', help='Will list the available servers and if they are active')
    async def listServers(self):
        # Call all of the servers which can be affected
        return

    @commands.command(name='ping', help='Pings the server and tells you the response rate')
    async def pingServer(self):
        # Pings server and send message of the response rate
        return

