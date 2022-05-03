import datetime
import json
import os
import logging

import discord
from discord.ext import commands

LOGGER = logging.getLogger(__name__)


class TimeKeepCommands(commands.Cog):
    jsonStructure = []
    filename = os.getenv("meeting_filename", "meetingOutput.txt")

    @commands.command(name='meeting', help='Tells the bot to join the voice channel')
    async def add_meeting(self, ctx, *, user_input):
        dateReferenceSplit = self.split_meeting_input(user_input)
        enteredDate = {"Date": dateReferenceSplit[0],
                       "Reference": dateReferenceSplit[1]}
        self.jsonStructure.append(enteredDate)
        LOGGER.warning("A Meeting was added on: '{0}'".format(enteredDate))
        self.sort_json()

    def sort_json(self):
        newlist = sorted(self.jsonStructure, key=lambda d: d["Date"])
        self.jsonStructure = newlist
        self.write_to_file()
        LOGGER.info("Json Sorted: '{0}'".format(self.jsonStructure))

    @commands.command(name='calendar', help='Prints out all of the upcoming meetings')
    async def list_meetings(self, ctx):
        self.read_from_file()
        embedMessage = discord.Embed(title="List of upcoming events")

        for item in self.jsonStructure:
            datetimeString = datetime.datetime.strptime(item["Date"], '%d/%m/%Y')
            if datetimeString > datetime.datetime.today():
                embedMessage.add_field(name=item["Date"], value=item['Reference'], inline=False)
        await ctx.send(embed=embedMessage)

    @commands.command(name='inRange', help='Prints all of the meetings between dates entered')
    async def in_range(self, startDate, endDate):
        # print queue of meetings in range
        LOGGER.error("in_range not yet implemented.")

    def write_to_file(self):
        with open(self.filename, 'w') as file:
            file.write(json.dumps(self.jsonStructure, indent=4, default=str))
        LOGGER.info("The json was written to file: '{0}'".format(self.filename))
        return self.filename

    def read_from_file(self):
        self.jsonStructure = []
        file = open(self.filename)
        data = json.load(file)
        for i in range(len(data)):
            self.jsonStructure.append(data[i])
        file.close()
        LOGGER.info("Json was read from file. Json: '{0}'".format(self.jsonStructure))

    def split_meeting_input(self, user_input):
        return str(user_input).split(" ")
