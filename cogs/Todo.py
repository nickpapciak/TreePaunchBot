import discord
from discord.ext import commands, menus
from discord.ext.commands import has_permissions, CheckFailure, CommandNotFound

from datetime import datetime
import json

from OtherFiles.todo_util import todo_add, todo_view, todo_delete
from main import TreePaunchBot


FILEPATH = "Data/todos.json"

# creates a source class for the menus module
class TodoMenuSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=6)

    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1
        # sends the correct page 
        embed_text = '\n'.join(f'{index}. {item}' for index, item in enumerate(entries, start=offset))
        return discord.Embed(description = embed_text, colour =  TreePaunchBot.color)

class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def todo_logger(self): 
      with open(FILEPATH , "r") as f: 
        dict = json.load(f)

        url_key = await self.bot.session.post("https://mystb.in/documents", data = json.dumps(dict, indent=6))
        url_key = await url_key.json()

      channel = self.bot.get_channel(735989735792705616)
      todo_embed = discord.Embed(
        title = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        url = f"https://mystb.in/{url_key['key']}.json", 
        colour =  self.bot.color)
      await channel.send(embed=todo_embed)

    @commands.group(aliases = ['t'], case_insensitive=True)
    async def todo(self, ctx):
        """TODO command that allows a user to store tasks"""


    @todo.command(name = "add", aliases = ["create", "start"])
    async def todo_add_cmd(self, ctx, *, todo=None): 
      if todo is None: 
        added_todo = "No todo was specified."
      else:
        added_todo = todo_add(str(ctx.author.id), str(todo))
      todo_embed = discord.Embed(
        description = added_todo, 
        colour =  self.bot.color)
      await ctx.send(embed=todo_embed)
      await self.todo_logger()

    @todo.command(name = "view", aliases = ["see", "check", "list"])
    async def todo_view_cmd(self, ctx): 
      todo_list = todo_view(str(ctx.author.id)) # generates a list of todo's

      if todo_list == []: #if the list is empty
        todo_embed = discord.Embed(
          description = "You have nothing in your todo list!", 
          colour =  self.bot.color)
        await ctx.send(embed=todo_embed)
      else: 
        pages = menus.MenuPages(source=TodoMenuSource(todo_list), clear_reactions_after=True) # creates a menu
        await pages.start(ctx)
        await self.todo_logger()

    @todo.command(name = "delete", aliases = ["del", "remove", "end", "finish"])
    async def todo_delete_cmd(self, ctx, index=None): 
      if index is None: 
        deleted_todo = "No index specified."
      else: 
        deleted_todo = todo_delete(str(ctx.author.id), index)
      todo_embed = discord.Embed(
        description = deleted_todo, 
        colour =  self.bot.color)
      await ctx.send(embed=todo_embed)
      await self.todo_logger()

def setup(bot):
    bot.add_cog(Todo(bot))



