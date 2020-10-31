import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, CommandNotFound
import aiohttp



class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='selfpurge')
    @commands.is_owner()
    async def purge_own(self, ctx, ids: commands.Greedy[int] = None):
        if ids is None:
            [await m.delete() async for m in ctx.channel.history(limit=5) if m.author == ctx.me]
            return
        with suppress(Exception):
            for i in ids:
                await (await ctx.channel.fetch_message(i)).delete()   

    @commands.command()
    async def f(self, ctx):
      """Press it to pay respects"""
      player_message = ctx.message
      await ctx.message.delete()

      embed = discord.Embed(
          description="""⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⢀⡤⢶⣶⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⢀⣠⣤⣤⣤⣿⣧⣀⣀⣀⣀⣀⣀⣀⣀⣤⡄⠀
  ⢠⣾⡟⠋⠁⠀⠀⣸⠇⠈⣿⣿⡟⠉⠉⠉⠙⠻⣿⡀
  ⢺⣿⡀⠀⠀⢀⡴⠋⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠙⠇
  ⠈⠛⠿⠶⠚⠋⣀⣤⣤⣤⣿⣿⣇⣀⣀⣴⡆⠀⠀⠀
  ⠀⠀⠀⠀⠠⡞⠋⠀⠀⠀⣿⣿⡏⠉⠛⠻⣿⡀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⣿⣿⡇⠀⠀⠀⠈⠁⠀⠀
  ⠀⠀⣠⣶⣶⣶⣶⡄⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀
  ⠀⢰⣿⠟⠉⠙⢿⡟⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀
  ⠀⢸⡟⠀⠀⠀⠘⠀⠀⠀⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
  ⠀⠈⢿⡄⠀⠀⠀⠀⠀⣼⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠙⠷⠶⠶⠶⠿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  
                  """,
          colour= self.bot.color)
      embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
      await ctx.send(embed=embed)
  
    @commands.command(aliases=['c'])
    @commands.is_owner()
    async def clear(self, ctx, amount: int = 1):
        """Bulk clear a specified amount of messages"""
        if ctx.invoked_subcommand is None:
          if amount <= 100:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
          else: 
            error_message = ctx.send("Cannot delete more than 100 messages")
            await error_message.delete()

def setup(bot):
    bot.add_cog(fun(bot))



