from discord.ext import commands
import discord
from cogs.utils import checks, context, db
from cogs.utils.config import Config
import datetime
import re
import json
import asyncio
import traceback
import sys
import aiohttp
# import AnonymousPost
from collections import Counter, deque, defaultdict

import config
import asyncpg

description = """
AggyBot online and reporting for duty!
"""

initial_extensions = ['cogs.owner',
                      'cogs.rolekeeper',
                      'cogs.reminder',
                      'cogs.core']
                    # 'cogs.tags

class AggyBot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True

        # TODO: Consider the following
        # intents = discord.Intents(
        #     guilds=True,
        #     members=True,
        #     bans=True,
        #     emojis=True,
        #     voice_states=True,
        #     messages=True,
        #     reactions=True,
        # )

        super().__init__(command_prefix='>', description=description,
                         pm_help=None, help_attrs=dict(hidden=True),
                         fetch_offline_members=False, heartbeat_timeout=150.0,
                         allowed_mentions=allowed_mentions, intents=intents)

        self.client_id = config.client_id;
        self.session = aiohttp.ClientSession(loop=self.loop)

        self._prev_events = deque(maxlen=10)

        # Obtain the role ids.
        with open('ids.json') as role_file:
            role_data = json.load(role_file)

        self.prisonerID = role_data["prisoner"]
        self.colorsID = role_data["colors"]
        self.skillsID = role_data["skills"]
        self.modID = role_data["moderator"]

        self.admin_chan_ID = role_data["admin"]
        self.log_chan_ID = role_data["logging"]
        self.prog_chan_ID = role_data["progress"]
        self.anon_chan_ID = role_data["anonymous"]

        # Obtain the guild
        self.agdg_id = 121565307515961346
        #self.agdg = self.get_guild(121565307515961346)

        # Fetch channel objects
        # self.admin_channel = self.agdg.get_channel(self.admin_chan_ID)

        # Obtain the channel to log members leaving.
        # self.log_channel = self.agdg.get_channel(self.log_chan_ID)

        # Obtain the channel for anonymous posting.
        # self.anon_channel = self.agdg.get_channel(self.anon_chan_ID)


        # leave_channel = discord.utils.get(agdg.channels, id=leave_chan_ID)
        # print('Identified log channel.\tName:{0.name}\tID:{0.id}'.format(leave_channel))

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    @property
    def agdg(self):
        # print('GETTING THE GUILD @#Q)(%@#%()*@#()%@*#%)*@#)(%')
        return self.get_guild(self.agdg_id)

    @property
    def admin_channel(self):
        return self.agdg.get_channel(self.admin_chan_ID)

    @property
    def log_channel(self):
        return self.agdg.get_channel(self.log_chan_ID)

    async def on_ready(self):
        print('Bot ready!')
        print('Logged in as {0.user.name}'.format(self))

        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        print('Targeted guild is {0.name}'.format(self.agdg))

        print(f'Details: {self.user} (ID: {self.user.id})')

        # game = discord.Game("Maintenance")
        # await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)


        print('----------')

    async def on_member_remove(self, mem):

        # Calculate duration of stay
        # time_spent = datetime.utcnow() - mem.joined_at
        # print('Time spent on server: ' + time_spent)

        nickname = mem.nick
        if nickname is None:
            nickname = ""
        else:
            nickname = "(" + nickname + ")"
        for role in mem.roles:
            # Special reporting if they're a prisoner that's leaving/
            if role.id == self.prisonerID:
                print("A user **left** the server with the prisoner role.")
                # Obtain reference to moderator role
                mod_role_obj = discord.utils.get(mem.guild.roles, id=self.modID)
                await self.log_channel.send(
                    mod_role_obj.mention + " {} {} has **left** the server with the prisoner role.".format(mem,
                                                                                                           nickname))
                return
        await self.log_channel.send("{} {} has **left** the server.".format(mem, nickname))

    async def on_message_delete(self, message):

        if message.author == self.user:
            return

        if len(message.mentions) > 0 or len(message.role_mentions) > 0:
            # Check if the message was created more than 20 minutes ago.
            if (datetime.utcnow() - message.created_at).total_seconds() > 1200:
                return
            nickname = message.author.nick
            if nickname is None:
                nickname = ""
            else:
                nickname = "(" + nickname + ")"
            await self.log_channel.send(
                '**User: **{} {} in {} | ``Delete``\n**Message: **{}'.format(message.author, nickname,
                                                                             message.channel.mention,
                                                                             message.content))

    async def on_message_edit(self, before, after):

        if before.author == self.user:
            return

        ping_before = len(before.mentions) > 0 or len(before.role_mentions) > 0
        ping_after = len(after.mentions) > 0 or len(after.role_mentions) > 0
        if ping_before and not ping_after:
            unickname = before.author.nick
            if unickname is None:
               unickname = ""
            else:
                unickname = "(" + unickname + ")"
            await self.log_channel.send(
                '**User: **{} {} in {} | ``Edit``\n**Message: **{}'.format(before.author, unickname,
                                                                           before.channel.mention,
                                                                           before.content))

    async def on_command_error(self, ctx, err):
        # Most logic borrowed from: https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        # Any commands with local error handlers will refer to that protocol instead.
        if hasattr(ctx.command, 'on_error'):
            return

        # Checks for original exceptions raised and sent to CommandInvokeError.
        err = getattr(err, 'original', err)

        # These are common errors that will log with benign consequences.
        # Anything in ignored will return and prevent anything happening.
        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(err, ignored):
            return

        elif isinstance(err, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(err, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.Forbidden:
                pass

        # All other commands are handled as default here.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(err), err, err.__traceback__, file=sys.stderr)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return
        #
        # bucket = self.spam_control.get_bucket(message)
        # current = message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
        # retry_after = bucket.update_rate_limit(current)
        # author_id = message.author.id
        # if retry_after and author_id != self.owner_id:
        #     self._auto_spam_count[author_id] += 1
        #     if self._auto_spam_count[author_id] >= 5:
        #         await self.add_to_blacklist(author_id)
        #         del self._auto_spam_count[author_id]
        #         await self.log_spammer(ctx, message, retry_after, autoblock=True)
        #     else:
        #         self.log_spammer(ctx, message, retry_after)
        #     return
        # else:
        #     self._auto_spam_count.pop(author_id, None)

        try:
            await self.invoke(ctx)
        finally:
            # Just in case we have any outstanding DB connections
            await ctx.release()

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_socket_response(self, msg):
        self._prev_events.append(msg)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        try:
            super().run(config.token, reconnect=True)
        finally:
            with open('prev_events.log', 'w', encoding='utf-8') as fp:
                for data in self._prev_events:
                    try:
                        x = json.dumps(data, ensure_ascii=True, indent=4)
                    except:
                        fp.write(f'{data}\n')
                    else:
                        fp.write(f'{x}\n')

    @property
    def config(self):
        return __import__('config')

# # Attempt to setup the PostgreSQL pool
# loop = asyncio.get_event_loop()
# try:
#     pool = loop.run_until_complete(Table.create_pool(config.postgresql, command_timout=60))
# except Exception as e:
#     print('Could not set up PostreSQL. Exiting.')
#
# bot.pool = pool

# @bot.event
# async def on_member_join(mem):
#     potential_links = []
#     invites = await bot.agdg.invites()
#     for invite in invites:
#         if invite.uses != stored_invites.get(invite, -1):
#             await bot.log_channel.send(f'{mem} has **joined** the server. (Invite: {invite.code} - Created by: {invite.inviter})')
#             break
#         elif invite not in stored_invites or invite.uses == invite.max_uses:
#             potential_links.append(invite)
#
#     if len(potential_links) > 0:
#         ret_list = []
#         for plink in potential_links:
#             ret_list.append(f'Invite: {plink.code} - Created by: {plink.inviter}')
#         ret_string = '\n'.join(ret_list)
#         await bot.log_channel.send(f'{mem} has **joined** the server.\nPossible Invites:{ret_string}')
#
#     # Update the stored invite information to reflect the updated values.
#     stored_invites.clear()
#     for invite in invites:
#         stored_invites[invite] = invite.uses



# async def process_commands(message):
#     ctx = await bot.get_context(message, cls=context.Context)
#
#     if ctx.command is None:
#         return
#
#     async with ctx.acquire():
#         await bot.invoke(ctx)
#
#

