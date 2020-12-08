import discord
from discord.ext import commands, menus

import json
from main import TreePaunchBot

FILEPATH = "Data/watchlist.json"
COLOR_MAP = [0x90be6d, 0xf9c74f, 0xf8961e, 0xf3722c, 0xf94144]
PREFIX = TreePaunchBot.prefix 

def refresh_json(file, json_obj):
    file.seek(0)
    file.truncate()
    json.dump(json_obj, file, indent=2)

async def send_embed(ctx, text): 
  await ctx.send(embed=discord.Embed(description=text, colour=TreePaunchBot.color))

class WatchListMenuSource(menus.ListPageSource):
    """Source for CardMenu"""
    def __init__(self, levels):
        self.levels = levels
        super().__init__([*range(len(levels))], per_page=1)

    async def format_page(self, menu, page):
        return self.levels[page]


class Watchlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(aliases = ['wl'], case_insensitive=True)
    @commands.has_any_role('Community Manager', 'Owner')
    async def watchlist(self, ctx):
      """Watchlist commands that allows storage of users to look out for"""

      if ctx.invoked_subcommand is None:
        wl_notes_embed = discord.Embed(
          title = "**Help for watchlist**",
          description = f"<required argument>\n[optional argument]\n\n**Aliases:** \n• watchlist - wl\n• add - a\n• delete - del - d - remove - rem - r\n• edit - e - change - c\n• view - v\n\nFor help with watchlist note commands do {PREFIX}watchlist notes\n\n",
          colour = self.bot.color
        )

        wl_notes_embed.add_field(name="**watchlist add <user> <level> [notes]**", 
        value=f"• Adds a user to the watchlist to the specified level\n• Can add notes as an optional argument\n• ex: `{PREFIX}wl add Narfee 3 for being not epic`", 
        inline = False)

        wl_notes_embed.add_field(name="**watchlist remove <user>**",
        value=f"• Deletes a user from the watchlist\n• ex: `{PREFIX}wl rem Narfee`", 
        inline = False)

        wl_notes_embed.add_field(name="**watchlist change <user> <level>**",
        value=f"• Changes the level of a user in the watchlist to another level\n• ex: `{PREFIX}wl c Narfee 5`", 
        inline = False)

        wl_notes_embed.add_field(name="**watchlist view**",
        value=f"• Shows the watchlist\n• ex: `{PREFIX}wl v`", 
        inline = False)

        await ctx.send(embed = wl_notes_embed)

    @watchlist.command(name = "view", aliases = ["v"])
    async def watchlist_view_cmd(self, ctx): 

      with open(FILEPATH, "r") as watchlist_file:
        wl_list = json.load(watchlist_file)
        if wl_list == []:
          await send_embed(ctx, "Watchlist is empty")
          return
      # creates the string text for each embed
      level_map = ["" for x in range(5)]
      for user in wl_list:
        print(user)
        notes = "\n".join(["> • "+item for item in user["notes"]])
        try:
          name = ctx.guild.get_member(int(user['id'])).nick or ctx.guild.get_member(int(user['id'])).name
          info_send = f"\n**{name}: **\n{notes if notes else '> No notes'}\n"
          level_map[user["level"]-1] += info_send
        except:
          pass

      # creates the embeds to send 
      embed_list = []
      for i, level_text in enumerate(level_map): 
        if level_text:
          wl_embed = discord.Embed(
            title = f'**__Watchlist__**', 
            description = level_text, 
            colour = COLOR_MAP[i])
          embed_list.append(wl_embed)

      # sends a list of embeds
      pages = menus.MenuPages(source=WatchListMenuSource(embed_list), clear_reactions_after=True)
      await pages.start(ctx)

    @watchlist.command(name = "add", aliases = ["a"])
    async def watchlist_add_cmd(self, ctx, user : discord.Member, level=None, *, notes=None): 
      if level is None: 
        await send_embed(ctx, "Please add the level you would like the user to be placed on")
        return 
      notes = [] if notes is None else [notes]
      with open(FILEPATH, "r+") as watchlist_file:
        wl_list = json.load(watchlist_file)

        if user.id not in [user["id"] for user in wl_list]:
          wl_list.append({"id": user.id, "level":int(level), "notes":notes})
          refresh_json(watchlist_file, wl_list)
          name = user.nick or user.name
          await send_embed(ctx, f"{name} was added to watchlist")
        else: 
          await send_embed(ctx, "User already in watchlist")


    @watchlist.command(name = "change", aliases = ["edit", "c"])
    async def watchlist_change_cmd(self, ctx, user : discord.Member, level : int = None): 
      if level is None: 
        await send_embed(ctx, "Please add the level you would like the user to be changed to")
        return
      
      with open(FILEPATH, "r+") as watchlist_file:
        wl_list = json.load(watchlist_file)

        for person in wl_list:
          if user.id == person["id"]:
            person["level"] = level

            refresh_json(watchlist_file, wl_list)
            name = user.nick or user.name
            await send_embed(ctx, f"{name}'s level was moved to {level}")
            break
        else: 
          await send_embed(ctx, "User not in watchlist")

    @watchlist.command(name = "remove", aliases = ["rem", "r", "delete", "del", "d"])
    async def watchlist_remove_cmd(self, ctx, user : discord.Member = None): 
      if user is None: 
        await send_embed(ctx, "Please add the user you would like to remove")
        return
      
      with open(FILEPATH, "r+") as watchlist_file:
        wl_list = json.load(watchlist_file)

        for i, person in enumerate(wl_list):
          if user.id == person["id"]:
            del wl_list[i]

            refresh_json(watchlist_file, wl_list)
            name = user.nick or user.name
            await send_embed(ctx, f"{name} was removed from watchlist")
            break
        else: 
          await send_embed(ctx, "User not in watchlist")


    @watchlist_add_cmd.error
    async def add_cmd_error(self, ctx, error):
      if isinstance(error, commands.BadArgument):
        await send_embed(ctx, "Could not find user")


    @watchlist.group(aliases = ['n', 'note'], case_insensitive=True)
    async def notes(self, ctx):
      """Watchlist commands that allows storage of users to look out for"""
      if ctx.invoked_subcommand is None:
        wl_notes_embed = discord.Embed(
          title = "**Help for watchlist notes**", 
          description = f"<required argument>\n\n**Aliases:** \n• watchlist - wl\n• notes - note - n\n• add - a\n• delete - del - d - remove - rem - r\n• edit - e - change - c\n\nFor help with regular watchlist commands do {PREFIX}watchlist\n\n",
          colour = self.bot.color
        )

        wl_notes_embed.add_field(name="**watchlist notes add <user> <note>**", 
        value=f"• Adds notes to a certain user in the watchlist\n• ex: `{PREFIX}wl a Narfee for being unepic`", 
        inline = False)

        wl_notes_embed.add_field(name="**watchlist notes delete <user> <note number>**",
        value=f"• deletes notes from a certain user in the watchlist\n• ex: `{PREFIX}wl del Narfee 2`", 
        inline = False)

        wl_notes_embed.add_field(name="**watchlist notes edit <user> <note number> <new text>**",
        value=f"• edits notes for a certain user in the watchlist\n• ex: `{PREFIX}wl e Narfee 1 for being *super* unepic`",
        inline = False)

        await ctx.send(embed = wl_notes_embed)


    @notes.command(name = "edit", aliases = ["change", "e", "c"])
    async def watchlist__note_edit_cmd(self, ctx, user : discord.Member, note_num : int , *, new_text=None): 
      with open(FILEPATH, "r+") as watchlist_file:
        wl_list = json.load(watchlist_file)

        for i, person in enumerate(wl_list):
          if user.id == person["id"]:
            try:
              if note_num < 1:
                raise IndexError
              wl_list[i]["notes"][note_num-1] = new_text
              await send_embed(ctx, f"Edited note {note_num}")
            except IndexError: 
              await send_embed(ctx, f"Note {note_num} doesn't exist")
            
        refresh_json(watchlist_file, wl_list)
        
    @notes.command(name = "delete", aliases = ["del", "d", "remove", "r", "rem"])
    async def watchlist_note_del_cmd(self, ctx, user : discord.Member, note_num : int): 
      with open(FILEPATH, "r+") as watchlist_file:
        wl_list = json.load(watchlist_file)

        for i, person in enumerate(wl_list):
          if user.id == person["id"]:
            try:
              if note_num < 1:
                raise IndexError
              del wl_list[i]["notes"][note_num-1]
              await send_embed(ctx, f"Deleted note {note_num}")
            except IndexError: 
              await send_embed(ctx, f"Note {note_num} doesn't exist")
            
        refresh_json(watchlist_file, wl_list)

    @notes.command(name = "add", aliases = ["a"])
    async def watchlist_note_add_cmd(self, ctx, user : discord.Member, *, note): 
      with open(FILEPATH, "r+") as watchlist_file:
        wl_list = json.load(watchlist_file)

        for i, person in enumerate(wl_list):
          if user.id == person["id"]:
            wl_list[i]["notes"].append(note)
            await send_embed(ctx, f"Note added")
        refresh_json(watchlist_file, wl_list)


# TODO: EXPERIMENT WITH DEFAULT SUBCOMMANDS WITH ctx.invoked_subcommand


def setup(bot):
    bot.add_cog(Watchlist(bot))



