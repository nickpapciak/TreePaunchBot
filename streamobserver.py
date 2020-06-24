import os
from contextlib import suppress
import secrets
import asyncio
from collections import namedtuple
from types import SimpleNamespace

from discord.ext import commands, tasks
import discord

# Define constants
CLIENT_ID = os.environ.get("CLIENT_ID")  # hey dont steal my client secret
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

STREAMER_DICT = {
  'TTV_Darklinggammer': 448865942634496020,
  'PandaSmoke': 161526961439637504,
  'SorlynLive': 176847780671782922,
  'T_Sori': 140659753616408576,
  'zeelinuxguy': 356948290169864204,
}

TokenData = namedtuple("TokenData", 'access_token _time_to_wait')

class TwitchClient:
    def __init__(self, *, session, client_id, client_secret):
        self.session = session
        self.client_id = client_id
        self.client_secret = client_secret

    async def get_access_token(self):
        async with self.session.post(
                f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}&client_secret={self.client_secret}&grant_type"
                f"=client_credentials") as post:
            data = await post.json()
        access_token = data.get('access_token')
        _time_to_wait = data.get('expires_in')
        return TokenData(access_token=access_token, _time_to_wait=_time_to_wait)


class StreamObserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_streamers = set()
        self.pfp_cache = dict()
        self.search_for_streams.start()
        self.t_client = TwitchClient(session=bot.session, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        bot.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        while True:
            tdata = await self.t_client.get_access_token()
            self.token = tdata.access_token
            self.bot.logger.info(f"Generated new twitch access token - {self.token} with {tdata._time_to_wait} seconds until expiration")
            await asyncio.sleep(tdata._time_to_wait - 5)

    async def _cache_streamer_pfps(self):
        for streamer_name in STREAMER_DICT.keys():
            async with self.bot.session.get(f'https://api.twitch.tv/helix/users/',
                                            params={'login': streamer}
                                            headers=request_headers) as resp:
                response = await resp.json()
                streamer_pfp = response['data'][0].get('profile_image_url')
                self.pfp_cache.update(streamer_name=streamer_pfp)

    def cog_unload(self):
        self.search_for_streams.cancel()

    async def get_stream_embed(self, streamer): 
        '''Gets information about a streamer and returns it in the form of an embed if possible 

        Args: 
            streamer (str): the login name of the current streamer
        
        Returns: 
            (discord.Embed): An embed with information about a stream
            False (bool): Returns false if streamer is not streaming
        '''
        request_headers = {'Client-ID': self.t_client.client_id, 'Authorization': f'Bearer {self.token}'}
      
        # requests data about the streamer
        async with self.bot.session.get(f'https://api.twitch.tv/helix/streams/?user_login={streamer}',
                                        headers=request_headers'}) as resp:
            response = await resp.json()
            if not response['data']: # returns False is streamer is offline
              return False 
            data = response['data'][0]
            # gets the url of the thumbnail
            data = SimpleNamespace(**data)
            data.thumbnail_url = URL(data.thumbnail_url.format(width=1920, height=1080)).update_query(secrets.token_urlsafe(5)) 
            view_word = "viewers" if data.viewer_count != 1 else "viewer"

        # this is used to find the name of the game from the id
        async with self.bot.session.get(f'https://api.twitch.tv/helix/games/',
                                        params={'id': data['game_id']}
                                        headers=request_headers) as resp:
            response = await resp.json()
            game = response['data'][0]['name']
        # creates the embed
        embed = discord.Embed(
          title = data.title,
          url = f'https://twitch.tv/{streamer}',
          description = f"Playing: {game}\n{data.viewer_count:,} {view_word}", 
          colour = 0x2ee863,
        )
        embed.set_image(url=data.thumbnail_url)
        embed.set_author(name = f"{data.user_name} is now live! Come show your support!", icon_url=self.pfp_cache[streamer])
        return embed

      
    @tasks.loop(seconds=10.0)
    async def search_for_streams(self):
      
        channel = self.bot.get_channel(720473926983221340)# tp --> 708832516177395833
        guild = self.bot.get_guild(618791723572658176) # tp --> 618791723572658176
        streaming_role = guild.get_role(720473746288410644) #tp --> 720473746288410644

        for streamer in STREAMER_DICT.keys(): # goes through the dict of streamers
          stream_embed = await self.get_stream_embed(streamer) #generates the embed
          if streamer not in self.active_streamers: # if the streamer is not already in the set 
            if stream_embed: # if they are streaming
              await channel.send(embed = stream_embed)
              self.active_streamers.add(streamer) # adds the streamer to the set 
              await guild.get_member(STREAMER_DICT[streamer]).add_roles(streaming_role) # gives roles
          else: # if they are already in the set 
            if not stream_embed: # if they are no longer streaming
              self.active_streamers.discard(streamer)
              await guild.get_member(STREAMER_DICT[streamer]).remove_roles(streaming_role) #removes roles

        # second check so if the bot goes offline then it removes streamer role
        for streamer in STREAMER_DICT.keys(): 
          if streamer not in self.active_streamers: 
            with suppress(Exception):
              await guild.get_member(STREAMER_DICT[streamer]).remove_roles(streaming_role)

    @search_for_streams.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @commands.command(name='drop')
    @commands.is_owner()
    async def drop_streamer_cache(self, ctx):
        self.active_streamers.clear()
        await ctx.send('Dropped streamer cache')

    @commands.command(name='show')
    @commands.is_owner()
    async def show_streamer_cache(self, ctx):
        await ctx.send(str(self.active_streamers))


    @commands.command()
    @commands.is_owner()
    async def manage_roles(self, ctx):
        await ctx.send(f'```{ctx.guild.roles}```')
        guild = self.bot.get_guild(618791723572658176)
        member = guild.get_member(258013196592349184)
        role = guild.get_role(720473746288410644)
        await member.add_roles(role)

    @commands.command(name='selfpurge')
    @commands.is_owner()
    async def purge_own(self, ctx, ids: commands.Greedy[int] = None):
        if ids is None:
            [await m.delete() async for m in ctx.channel.history(limit=5) if m.author == ctx.me]
            return
        with suppress(Exception):
            for i in ids:
                await (await ctx.channel.fetch_message(i)).delete()   

def setup(bot):
    bot.add_cog(StreamObserver(bot))

