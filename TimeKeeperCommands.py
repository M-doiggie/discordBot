import os

from discord.ext import commands
import json


class TimeKeepCommands(commands.Cog):
    jsonStructure = []
    filename = os.getenv("meetingOutput.txt")

    @commands.command(name='meeting', help='Tells the bot to join the voice channel')
    async def add_meeting(self, date, reference):
        date = {"Date": date,
                "Reference": reference}
        self.jsonStructure.append(date)
        print("join")

    @add_meeting.after_invoke
    async def after_sort(self):
        self.sort_json()

    def sort_json(self):
        newlist = sorted(self.jsonStructure, key=lambda d: d["Date"])
        self.jsonStructure = newlist
        self.write_to_file()

    @commands.command(name='calendar', help='Prints out all of the upcoming meetings')
    async def list_meetings(self, date, reference):
        # print queue of upcoming meetings
        print("Print a queue of meetings")

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
        file = open(self.filename)
        data = json.load(file)
        for i in range(len(data)):
            self.jsonStructure.append(data[i])
        file.close()
