import os
import logging

import aiohttp
import asyncio
import discord
from discord.ext import commands

from config.config import TOKEN

from OtherFiles.webserver import keep_alive
from OtherFiles.general_util import load_cogs, load_menu
import OtherFiles.mobile_indicator
4
# logging.basicConfig(level=logging.INFO)
load_menu()
PREFIX = "!!"

# intents garbage
intents = discord.Intents.default()
intents.members = True


class TreePaunchBot(commands.Bot):
    color = 0x2ee863
    prefix = PREFIX

    def __init__(self):
        super().__init__(command_prefix=PREFIX, case_insensitive=True, intents=intents)
        self.remove_command("help")
        self.prefix = PREFIX
        self.color = 0x2ee863
        self.owner_ids = [680835476034551925,
                          258013196592349184, 140659753616408576]
        self.session = aiohttp.ClientSession()
        load_cogs(self)
        print("TreePaunchBot started")


if __name__ == "__main__":
    keep_alive()
    TreePaunchBot().run(TOKEN)
