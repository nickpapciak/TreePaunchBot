import os
from discord.ext import commands, tasks
import discord

# Define constants
CLIENT_ID = os.environ.get("CLIENT_ID")  # hey dont steal my client secret
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")


class StreamObserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_streamers = set()
        self.search_for_streams.start() 


    def cog_unload(self):
        self.search_for_streams.cancel()

    async def get_profile_image(self, twitchname):
        """Yes, all this does is get the profile image of the twith user.
        Yes, you could just take the discord user's image. Yes you could just
        send the link and have the automatic embed, but here in narfville
        we don't cut corners, exept we do but I just wanted it to look nice
        in the embed so here we are ok this docstring is too long bye"""

        # gets access token or something idk I should prob learn requests and aiohttp more
        async with self.bot.session.post(
                f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type"
                f"=client_credentials") as post:
            token = (await post.json()).get('access_token')

        # requests image url from twitch api
        async with self.bot.session.get(f'https://api.twitch.tv/helix/users/?login={twitchname}',
                                        headers={'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}) as resp:
            response = await resp.json()
            return response['data'][0].get('profile_image_url')

    @staticmethod
    def check_stream_continued(member):
        return any([isinstance(a, discord.Streaming) for a in member.activities])

    @tasks.loop(seconds=10.0)
    async def search_for_streams(self):

        # two treepaunch channels
        channel = self.bot.get_channel(708832516177395833)
        guild = self.bot.get_guild(618791723572658176)

        humans = [member for member in guild.members if not member.bot]

        # checks all the users in ths server for streaming statuses
        for member in humans:
            for activity in member.activities:
                if isinstance(activity, discord.Streaming):

                    if member not in self.active_streamers:
                        # this is necessary to get the twitch name
                        twitch_name = activity.assets['large_image'][7:]

                        # this is just the embed it makes it look nice, say hi to embed everyone
                        embed = discord.Embed(
                            title=f"{twitch_name} is streaming {activity.game} on {activity.platform}. Come say hi!",
                            description=f"{activity.url}"
                        )

                        # I made it a function to hide the pain of the code above and also so it doesn't look trash
                        image_url = await self.get_profile_image(twitch_name)
                        embed.set_image(url=image_url)
                        await channel.send(embed=embed)
                        self.active_streamers.add(member)  # this is kinda janky might use json later

        # goes through the set and sees if anyone has stopped streaming
        [self.active_streamers.discard(member) for member in frozenset(self.active_streamers) if not
            self.check_stream_continued(member)]

    @search_for_streams.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @commands.command(name='drop')
    @commands.is_owner()
    async def drop_streamer_cache(self, ctx):
        self.active_streamers.clear()
        await ctx.send('Dropped streamer cache')

    @commands.command(name='selfpurge')
    @commands.is_owner()
    async def purge_own(self, ctx, ids: commands.Greedy[int] = None):
        if ids is None:
            [await m.delete() async for m in ctx.channel.history(limit=5) if m.author == ctx.me]
            return
        msgs = [await ctx.channel.fetch_message(i) for i in ids]
        await ctx.channel.delete_messages(msgs)       

def setup(bot):
    bot.add_cog(StreamObserver(bot))

