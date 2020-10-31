import os
import logging

import aiohttp
import asyncio
from discord.ext import commands

from OtherFiles.webserver import keep_alive
from OtherFiles.general_util import load_cogs, load_menu

logging.basicConfig(level=logging.INFO)


class TreePaunchBot(commands.Bot):
  color = 0x2ee863

  def __init__(self):
      super().__init__(command_prefix='!!', case_insensitive=True)
      self.remove_command("help")
      self.color = 0x2ee863
      self.owner_ids = [680835476034551925, 258013196592349184, 140659753616408576]
      self.session = aiohttp.ClientSession()
      load_cogs(self)
      print("TreePaunchBot started")



if __name__ == "__main__":
  keep_alive()
  TOKEN = os.environ.get("DISCORD_TOKEN")
  TreePaunchBot().run(TOKEN)

