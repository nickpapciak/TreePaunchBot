import os
from contextlib import suppress
from discord.ext import commands, tasks
import discord
import secrets

# Define constants
CLIENT_ID = os.environ.get("CLIENT_ID")  # hey dont steal my client secret
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

STREAMER_DICT = {
  'TTV_Darklinggammer': 448865942634496020,
  'PandaSmoke': 161526961439637504,
  'SorlynLive': 176847780671782922,
  'T_Sori': 140659753616408576,
  'narfeepap' : 258013196592349184
}


class StreamObserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_streamers = set()
        self.search_for_streams.start() 


    def cog_unload(self):
        self.search_for_streams.cancel()

  
    async def get_stream_embed(self, streamer): 
        '''Gets information about a streamer and returns it in the form of an embed if possible 

        Args: 
            streamer (str): the login name of the current streamer
        
        Returns: 
            (discord.Embed): An embed with information about a stream

        Raises: 
            False (bool): Returns false if streamer is not streaming
        '''
      

        # I'm not super familiar with aiohttp so don't crucify me if this is a terrible way of doing it :/


        #gets authorization to the twitch api
        async with self.bot.session.post(
                f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type"
                f"=client_credentials") as post:
            token = (await post.json()).get('access_token')
  
        # requests data about the streamer
        async with self.bot.session.get(f'https://api.twitch.tv/helix/streams/?user_login={streamer}',
                                        headers={'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}) as resp:
            response = await resp.json()
            try:
              if not response['data']: # returns False is streamer is offline
                return False 
            except: 
              return False
              print(response)
            data = response['data'][0]

            # gets the url of the thumbnail
            thumbnail_url = data['thumbnail_url'].format(width=1920, height=1080) + f"?{secrets.token_urlsafe(5)}" # <-- thats what streamcord does I wasn't able to figure it out myself 
            twitch_name = data['user_name'] 
            viewer_count = data['viewer_count']
            stream_name = data['title']
            view_word = "viewers" if viewer_count != 1 else "viewer"
            
        # this is used to find the name of the game from the id
        async with self.bot.session.get(f'https://api.twitch.tv/helix/games/?id={data["game_id"]}',
                                        headers={'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}) as resp:
            response = await resp.json()
            game = response['data'][0]['name']

        # this gets the streamer's pfp
        async with self.bot.session.get(f'https://api.twitch.tv/helix/users/?login={streamer}',
                                        headers={'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}) as resp:
            response = await resp.json()
            streamer_pfp = response['data'][0].get('profile_image_url')
        
        # creates the embed
        embed = discord.Embed(
          title = stream_name,
          url = f'https://twitch.tv/{streamer}',
          description = f"Playing: {game}\n{viewer_count:,} {view_word}", 
          colour = 0x2ee863,
        )
        embed.set_image(url=thumbnail_url)
        embed.set_author(name = f"{twitch_name} is now live! Come show your support!", icon_url = streamer_pfp)

        return embed

      
    @tasks.loop(seconds=10.0)
    async def search_for_streams(self):

      
        channel = self.bot.get_channel(708832516177395833)# tp --> 708832516177395833
        guild = self.bot.get_guild(618791723572658176) # tp --> 618791723572658176
        streaming_role = guild.get_role(720473746288410644) #tp --> 720473746288410644


        for streamer in STREAMER_DICT.keys(): # goes through the dict of streamers
          stream_embed = await StreamObserver.get_stream_embed(self, streamer) #generates the embed
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
            try: 
              await guild.get_member(STREAMER_DICT[streamer]).remove_roles(streaming_role)
            except: 
              pass


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
              colour=0x2ee863)
          embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
          await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StreamObserver(bot))

