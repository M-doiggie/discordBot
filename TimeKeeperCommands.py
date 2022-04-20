import datetime
import json
import os

import discord
from discord.ext import commands


class TimeKeepCommands(commands.Cog):
    jsonStructure = []
    filename = os.getenv("meeting_filename", "meetingOutput.txt")

    @commands.command(name='meeting', help='Tells the bot to join the voice channel')
    async def add_meeting(self, ctx, *, user_input):
        dateReferenceSplit = self.split_meeting_input(user_input)
        enteredDate = {"Date": dateReferenceSplit[0],
                       "Reference": dateReferenceSplit[1]}
        print(user_input)
        print(enteredDate)
        self.jsonStructure.append(enteredDate)
        print("join")

    @add_meeting.after_invoke
    async def after_sort(self, ctx):
        self.sort_json()

    def sort_json(self):
        newlist = sorted(self.jsonStructure, key=lambda d: d["Date"])
        self.jsonStructure = newlist
        self.write_to_file()

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
        print("Print a queue of meetings")

    def write_to_file(self):
        with open(self.filename, 'w') as file:
            file.write(json.dumps(self.jsonStructure, indent=4, default=str))
        print("Wrote to " + self.filename)
        return self.filename

    def read_from_file(self):
        print("Start of read")
        self.jsonStructure = []
        file = open(self.filename)
        data = json.load(file)
        for i in range(len(data)):
            self.jsonStructure.append(data[i])
        file.close()
        print(self.jsonStructure)
        print("End of read")

    def split_meeting_input(self, user_input):
        return str(user_input).split(" ")
