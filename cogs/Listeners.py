import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, CommandNotFound
import asyncio

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):  
      if message.channel == self.bot.get_channel(618881405765681183):
        await message.add_reaction('<a:diamond:726193238905585684>')
        await message.add_reaction('<:coal:726193326885437480>')

      if message.content.lower() in ["hello there", "hello there.", "hello there!"]: 
        await message.add_reaction("<:hellothere:750879346633474118>")

        def check(reaction, user):
          return user == message.author and str(reaction.emoji) == '<:hellothere:750879346633474118>'

        try:
          reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

        except asyncio.TimeoutError:
          await message.clear_reaction('<:hellothere:750879346633474118>')
        else:
          await message.clear_reaction('<:hellothere:750879346633474118>')
          await message.channel.send('https://tenor.com/view/grevious-general-kenobi-star-wars-gif-11406339')

def setup(bot):
    bot.add_cog(Listeners(bot))



