async def mobile_id(self):
    from discord.gateway import log
    import sys
    """Sends the IDENTIFY packet."""
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'Discord iOS',
                '$device': 'discord.py',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'guild_subscriptions': self._connection.guild_subscriptions,
            'v': 3
        }
    }

    if not self._connection.is_bot:
        payload['d']['synced_guilds'] = []

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    
    #if state._intents is not None:
        #payload['d']['intents'] = state._intents.value

    #await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)

    await self.send_as_json(payload)
    log.info('Shard ID %s has sent the IDENTIFY payload.', self.shard_id)


import discord
discord.gateway.DiscordWebSocket.identify = mobile_id


# setattr(discord.gateway.DiscordWebSocket, "identify", mobile_id)