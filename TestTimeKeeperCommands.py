import os
from datetime import datetime, timedelta
from os.path import exists

import TimeKeeperCommands

today = datetime.today().strftime("%d/%m/%Y")
yesterday = datetime.today() - timedelta(days=1)
yesterday = yesterday.strftime("%d/%m/%Y")


def tear_down():
    if exists("meetingOutput.txt"):
        os.remove("meetingOutput.txt")


def test_write_to_file():
    commands = TimeKeeperCommands.TimeKeepCommands()
    commands.filename = "meetingOutput.txt"
    commands.jsonStructure = [{"Date": str(today), "Reference": "Party"},
                              {"Date": str(yesterday), "Reference": "Drinks"}]
    result = commands.write_to_file()
    assert exists(result) is True, "The file was not able to be made."


def test_sort_json():
    commands = TimeKeeperCommands.TimeKeepCommands()
    commands.filename = "meetingOutput.txt"

    commands.jsonStructure = [{"Date": today, "Reference": "Party"},
                              {"Date": yesterday, "Reference": "Drinking"}]

    commands.sort_json()
    assert commands.jsonStructure[0].get("Date") == yesterday, "json was not sorted"
    assert commands.jsonStructure[1].get("Date") == today, "json was not sorted"


def test_read_from_file():
    commands = TimeKeeperCommands.TimeKeepCommands()
    commands.jsonStructure = []
    commands.filename = "meetingOutput.txt"
    commands.read_from_file()

    assert commands.jsonStructure[0].get("Date") == yesterday, "Json was not read correctly"


if __name__ == '__main__':
    test_write_to_file()
    test_sort_json()
    test_read_from_file()
    tear_down()
