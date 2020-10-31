import os
import logging

import aiohttp
import asyncio
from discord.ext import commands

from OtherFiles.webserver import keep_alive
from OtherFiles.util import load_cogs, load_menu

logging.basicConfig(level=logging.INFO)


class TreePaunchBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!!', case_insensitive=True)
        self.remove_command("help")
        self.color = 0x2ee863
        self.owner_ids = [680835476034551925, 258013196592349184, 140659753616408576]
        self.session = aiohttp.ClientSession()
        load_cogs(self)
        print("TreePaunchBot started")



keep_alive()
TOKEN = os.environ.get("DISCORD_TOKEN")
TreePaunchBot().run(TOKEN)

