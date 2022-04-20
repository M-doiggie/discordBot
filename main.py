import MiscCommands
import MusicCommands
from datetime import datetime
import discord
from discord.ext import commands

# Auth Variables
# Mr botty token
#DISCORD_TOKEN = "ODE4NTYzNjQyMzcwNTU1OTM1.YEZ4zA.jP_pHO6v8rKcECr4hmVYfdbSM0E"
# test token
import TimeKeeperCommands

DISCORD_TOKEN = "OTE3MDU3NDQ5MTk2OTQxNDc1.YazKTQ.vyTD_6i4qSjuhkOPvB4vMB08hsM"

#used to retirve token from environment, allows for docker to have multipe bot instances for multiple server if required
#DISCORD_TOKEN = os.getenv("discord_token")

birdy_uri = ''

intents = discord.Intents().all()
client = discord.Client(intents=intents)
theBot = commands.Bot(command_prefix='!', intents=intents)

# Start and run of bot
theBot.add_cog(MusicCommands.MusicCommands())
theBot.add_cog(MiscCommands.MiscCommands())
theBot.add_cog(TimeKeeperCommands.TimeKeepCommands())

if __name__ == "__main__":
    print("Bot started up at: ", datetime.now(), flush=True)
    theBot.run(DISCORD_TOKEN)
