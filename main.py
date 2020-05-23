# I should pep8 this but its too far gone 
# thank god most of you don't understand this, this entire code is pretty braindead but 
# it works sooooo....

import discord
from webserver import keep_alive
from discord.ext import commands, tasks
import os
import aiohttp
import asyncio

client = commands.Bot(command_prefix="~")


# uh oh this is a global oh boy 
streaming = set()

async def get_profile_image(twitchname):
    '''Yes, all this does is get the profile image of the twith user. 
  Yes, you could just take the discord user's image. Yes you could just 
  send the link and have the automatic embed, but here in narfville 
  we don't cut corners, exept we do but I just wanted it to look nice 
  in the embed so here we are ok this docstring is too long bye''' 

    # opens an aiohttp session
    session = aiohttp.ClientSession()
    client_id = os.environ.get("CLIENT_ID") # hey dont steal my client secret 
    client_secret = os.environ.get("CLIENT_SECRET") 

    # gets access token or something idk I should prob learn requests and aiohttp more 
    async with session.post(f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials") as post:
      token = (await post.json()).get('access_token')

    # requests image url from twitch api
    async with session.get(f'https://api.twitch.tv/helix/users/?login={twitchname}', headers= {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}) as resp:
      response = await resp.json()
      await session.close()
      return response['data'][0].get('profile_image_url')

@client.event
async def on_ready():
  print("TreePaunchBot is ready")
  await search_for_streams.start() # starts this monstrosity 

# tells all errors to screw off 
@client.event
async def on_command_error(self, ctx, error):
  pass
 
@tasks.loop(seconds=10.0)
async def search_for_streams():
  global streaming # yes I use globals, please don't crucify me, I don't feel like making a json file

  # two treepaunch channels 
  channel = client.get_channel(708832516177395833)
  guild = client.get_guild(618791723572658176)
 

  # checks all the users in ths server for streaming statuses 
  for member in guild.members: 
    if not member.bot: # makes sure bots with custom status dont pass
      for activity in member.activities: 
        if isinstance(activity, discord.Streaming):
          
          if member not in streaming:

            # this is necessary to get the twitch name 
            twitchname = activity.assets['large_image'][7:]

            # this is just the embed it makes it look nice, say hi to embed everyone 
            embed = discord.Embed(
              title = f"{twitchname} is streaming {activity.game} on {activity.platform}. Come say hi!",
              description = f"{activity.url}"
            )

            # I made it a function to hide the pain of the code above and also so it doesn't look trash
            image_url = await get_profile_image(twitchname)
            embed.set_image(url=image_url)
            await channel.send(embed=embed)
            streaming.add(member) # this is kinda janky might use json later

  # goes through the set and sees if anyone has stopped streaming
  for member in list(streaming): 
    member_is_streaming = False # var name is way too long but if i don't name it like this i wont understand this next week lmao
    for activity in member.activities: 
      if isinstance(activity, discord.Streaming):
        member_is_streaming = True
    if not member_is_streaming: 
      streaming.discard(member) # also janky
      # print(f"{member.name} has finished streaming")
      # print(streaming)


keep_alive()
TOKEN = os.environ.get("DISCORD_TOKEN")
client.run(TOKEN)

