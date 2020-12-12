import os
from discord.ext import commands, tasks
import discord
import datetime
import json 

# define constants 
FILEPATH = "data/holidays.json"
MONTH_DICT= {
   1:"January",
   2:"February",
   3:"March",
   4:"April",
   5:"May",
   6:"June",
   7:"July",
   8:"August",
   9:"September",
   10:"October",
   11:"November",
   12:"December"
}
DAY_SUFFIX = {1:"st", 2:"nd", 3:"rd"}
with open(FILEPATH, "r+") as holiday_file: 
  EVENTS = json.load(holiday_file)

def generate_readable_day(day:str): 
  month = MONTH_DICT[int(day[:2])]
  numbered_date = int(day[3:])
  if numbered_date in [1, 2, 3, 21, 22, 23, 31]: 
    suffix = DAY_SUFFIX[numbered_date%10]
  else: 
    suffix = "th"
  return f"{month} {numbered_date}{suffix}"

def refresh_json(file, dict):
    file.seek(0)
    file.truncate()
    json.dump(dict, file, indent=2)


class HolidayObserver(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.holiday_checker.start()


  @tasks.loop(seconds=30)
  async def holiday_checker(self):
    """Checks for certain holidays"""
    channel = self.bot.get_channel(720473926983221340) #tp = 618791723572658179
    
    # gets the date to print it at 2:00pm cst 
    today = str(datetime.datetime.now() - datetime.timedelta(hours=20))[5:10]
    
    for day in EVENTS.keys(): 
      if day == today: 
        with open(FILEPATH, "r+") as holiday_file: 
          holiday_dict = json.load(holiday_file)

          if not holiday_dict[day]["has_triggered"]:
            message = "Wish them a happy birthday! 🎂 🥳" if "Birthday" in EVENTS[day] else "Let's celebrate 🥳"
            holidayEmbed = discord.Embed(
              description = f"Hey everyone, it's {EVENTS[day]['name']}! {message}", 
              colour =  self.bot.color,
            )
            await channel.send(embed=holidayEmbed)
            holiday_dict[day]["has_triggered"] = True
            refresh_json(holiday_file, holiday_dict)

    if today == "12-31": 
      with open(FILEPATH, "r+") as holiday_file: 
          holiday_dict = json.load(holiday_file)
          for key in holiday_dict.keys(): 
            holiday_dict[key]["has_triggered"] = False

          refresh_json(holiday_file, holiday_dict)

  @commands.command(aliases = ["next", "upcoming", "events"])
  async def _next(self, ctx): 
    with open(FILEPATH, "r") as holiday_file: 
        holiday_dict = json.load(holiday_file)

        for day, date_status in holiday_dict.items():

          if not date_status["has_triggered"]: 

            readable_day = generate_readable_day(day)

            next_holiday_embed = discord.Embed(
              description = f"The next holiday is **{EVENTS[day]['name']}** on **{readable_day}**. Get ready!", 
              colour =  self.bot.color,)
            await ctx.send(embed=next_holiday_embed)
            break
        else: 
          next_holiday_embed = discord.Embed(
              description = f"The next holiday is New Year's Day on Jan 1st. Don't lose your resolutions!", 
              colour =  self.bot.color,)
          await ctx.send(embed=next_holiday_embed)

  @holiday_checker.before_loop
  async def holiday_before(self):
      await self.bot.wait_until_ready()
  
def setup(bot):
    bot.add_cog(HolidayObserver(bot))

