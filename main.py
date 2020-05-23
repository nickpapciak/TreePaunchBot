# I should pep8 this but its too far gone 
# thank god most of you don't understand this, this entire code is pretty braindead but 
# it works sooooo....

import os

import aiohttp
from discord.ext import commands

from webserver import keep_alive


class StreamObserver(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='~')
        self.session = aiohttp.ClientSession()
        self.load_extension('observer')
        print("Bot initialising")

    async def on_command_error(self, ctx, error):
        print(error)
        return True


keep_alive()
TOKEN = os.environ.get("DISCORD_TOKEN")
StreamObserver().run(TOKEN)
