from discord.ext import commands
import discord
import asyncio

import math
import copy
import io

class Core(commands.Cog):
    """The original set of commands featured on AggyBot"""

    def __init__(self, bot):

        self.bot = bot
        # self.agdg = bot.agdg
        # TODO: bot.agdg is not being created properly for some reason.

    # @bot.command()
    # @commands.has_permissions(manage_roles=True)
    # async def showcolors(ctx):
    #     # for role in ctx.guild.roles:
    #     #     await ctx.send('{}-{}-{}'.format(role.name, role.position, role.id))
    #     await ctx.send('displaying all colors')
    #     colors = discord.utils.get(ctx.guild.roles, id=colorsID)
    #     skills = discord.utils.get(ctx.guild.roles, id=skillsID)
    #     if skills.position > colors.position:
    #         raise RuntimeError
    #     await ctx.send('positions are c{} and s{}'.format(colors.position, skills.position))
    #     # sorted_roles = sorted(ctx.guild.roles, key=lambda role: role.position, reverse=True)
    #     sorted_roles = sorted(ctx.guild.roles)
    #     for i in sorted_roles[skills.position+1: colors.position]:
    #         await ctx.send('{}-{}'.format(i.name, i.position))


    # @bot.command()
    # @commands.has_permissions(manage_roles=True)
    # async def showskills(ctx):
    #     await ctx.send('displaying all skills')
    #     skills = discord.utils.get(ctx.guild.roles, id=skillsID)
    #
    #     await ctx.send('position is s{} and {}'.format(skills.position, 0))
    #
    #     # Iterate through the sublist
    #     sorted_roles = sorted(ctx.guild.roles)
    #     for s in sorted_roles[:skills.position]:
#         await ctx.send('{}-{}'.format(s.name, s.position))

    @commands.command()
    async def color(self, ctx, col):
        # await ctx.send('Assigning color.')
        colors = discord.utils.get(self.bot.agdg.roles, id=self.bot.colorsID)
        skills = discord.utils.get(self.bot.agdg.roles, id=self.bot.skillsID)
        # await ctx.send('positions are c{} and s{}'.format(colors.position, skills.position))

        # Sort the list.
        sorted_roles = sorted(self.bot.agdg.roles)

        # Determine member (Allows for DMing the bot).
        mem = None
        if isinstance(ctx.channel, discord.DMChannel):
            mem = self.bot.agdg.get_member(ctx.author.id)
            if mem is None:
                # Why are you using my bot, huh?
                return
        else:
            mem = ctx.author

        # Iterate through the sublist
        for c in sorted_roles[skills.position + 1: colors.position]:

            if c.name.lower() == col.lower():
                await mem.add_roles(c)

                # Members can only have one color, so check if they already have a color role and replace it.
                for i in sorted_roles[skills.position + 1: colors.position]:
                    if i in mem.roles and i != c:
                        await mem.remove_roles(i)

                await ctx.message.add_reaction('✅')
                return

        await ctx.message.add_reaction('❌')

    @commands.command()
    async def addskill(self, ctx, *skills):

        skill_role = discord.utils.get(self.bot.agdg.roles, id=226331683996172288)

        # Make all the args lowercase.
        roles_not_added = []
        for s in skills:
            roles_not_added.append(s.lower())

        # Iterate through the role sublist
        roles_to_add = []
        sorted_roles = sorted(self.bot.agdg.roles)
        for s in sorted_roles[:skill_role.position]:
            if s.name.lower() in roles_not_added:
                roles_to_add.append(s)
                roles_not_added.remove(s.name.lower())

        # Add all of the successfully identified roles to the Member (and User -> Member if DM)
        if isinstance(ctx.channel, discord.DMChannel):
            mem = self.bot.agdg.get_member(ctx.author.id)
            if mem is not None:
                await mem.add_roles(*roles_to_add)
        else:
            await ctx.author.add_roles(*roles_to_add)

        # If any roles failed to be added, log which roles were added and which failed.
        if len(roles_not_added) > 0:
            if len(skills) > 1 and len(roles_not_added) < len(skills):
                for idx, role in enumerate(roles_to_add):
                    roles_to_add[idx] = role.name
                await ctx.send(f'Only role(s) {", ".join(roles_to_add)} added.')
            else:
                await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    @commands.command()
    async def removeskill(self, ctx, *skills):

        mem = None
        mem_roles = None
        if isinstance(ctx.channel, discord.DMChannel):
            mem = self.bot.agdg.get_member(ctx.author.id)
            if mem is None:
                # Why are you using my bot, huh?
                return
            else:
                mem_roles = mem.roles
        else:
            mem_roles = ctx.author.roles

        # Make all the args lowercase.
        roles_not_removed = []
        for s in skills:
            roles_not_removed.append(s.lower())

        # Prep the server role list so that users can't remove special use roles.
        sorted_list = sorted(self.bot.agdg.roles)
        skill_role = discord.utils.get(self.bot.agdg.roles, id=self.bot.skillsID)
        public_roles = sorted_list[:skill_role.position]

        # Iterate through the role sublist
        roles_to_verify = []
        # Ignore any roles outside of the skills bracket.
        for r in mem_roles:
            if r.name.lower() in roles_not_removed:
                roles_to_verify.append(r.name.lower())

        roles_to_remove = []
        for s in public_roles:
            if s.name.lower() in roles_to_verify:
                roles_to_remove.append(s)
                roles_not_removed.remove(s.name.lower())

        # Add all of the successfully identified roles to the Member (and User -> Member if DM)
        if isinstance(ctx.channel, discord.DMChannel):
            mem = ctx.guild.get_member(ctx.author.id)
            if mem is not None:
                await mem.remove_roles(*roles_to_remove)

        else:
            await ctx.author.remove_roles(*roles_to_remove)

        # If any roles failed to be removed, log which roles were removed and which failed.
        if len(roles_not_removed) > 0:
            if len(skills) > 1 and len(roles_not_removed) < len(skills):
                for idx, role in enumerate(roles_to_remove):
                    roles_to_remove[idx] = role.name
                await ctx.send(f'Only role(s) {", ".join(roles_to_remove)} removed.')
            else:
                await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def jail(self, ctx, member: discord.Member, time: int=30, *, reason=None):
        # await ctx.channel.send('Jailing {}'.format(member.display_name))
        jail_role = discord.utils.get(ctx.guild.roles, id=367155287343366144)
        mod_role = discord.utils.get(ctx.guild.roles, id=121566377063481344)

        if not member.top_role >= mod_role:

            await member.add_roles(jail_role, reason=reason)

            await ctx.message.add_reaction('✅')

            # Determine if the reason needs to be tacked on
            if reason is not None:
                full_reason = ' Reason: {}'.format(reason)
            else:
                full_reason = ''

            # TODO: Log the jailing to the audit log and json file.

            # Send out notifications on all appropriate channels.
            await self.bot.log_channel.send('**{}** was jailed for **{} minute(s)**'.format(member.display_name, time) + full_reason)

            # Wait the determined amount of time before removing the role.
            await asyncio.sleep(float(time*60))
            if jail_role in member.roles:
                await member.remove_roles(jail_role, reason="Automatic removal by bot.")
                await self.bot.log_channel.send(
                    '**{}** was unjailed automatically after **{} minutes(s)**'.format(member.display_name, time))
            else:
                await self.bot.log_channel.send(
                    'The jail time of **{} minutes(s)** expired for **{}** but their Prisoner role was already removed.'.format(time, member.display_name))

        ctx.message.add_reaction('❌')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unjail(self, ctx, member: discord.Member):
        await ctx.channel.send('Un-Jailing {}'.format(member.display_name))
        jail_role = discord.utils.get(ctx.guild.roles, id=367155287343366144)
        await member.remove_roles(jail_role)


    @commands.command()
    async def checkrole(self, ctx, *, arg1):
        if not ctx.guild.chunked:
            print('Server was chunked due to a checkrole invocation.')
            await ctx.guild.chunk()
        # print('Value of guild.chunked is {}'.format(ctx.guild.chunked))
        for role in ctx.guild.roles:
            if role.name.lower() == arg1.lower():
                await ctx.channel.send('There are {} users with the {} role.'.format(len(role.members), role.name))

    # # Dumb way to disable a command from source.
    # # TODO: Remove this check once anon command functionality is completed.
    # def anon_check(ctx):
    #     return False
    #
    #
    # @bot.command()
    # @commands.check(anon_check)
    # async def anon(ctx, *, cont):
    #
    #     # if(ctx.author)
    #
    #     # Wait for half a second to ensure embeds are logged properly
    #     # if not ctx.message.embeds and not ctx.message.attachments:
    #     #     await bot.wait_for('message_edit', timeout=1.5)
    #
    #     ac = bot.anon_channel
    #
    #     ret_id = await AnonymousPost.hash_id(str(ctx.author))
    #     await ctx.author.send('You are about to post the following message. To confirm or deny just reply with ✅ or ❌.')
    #     preview_msg = await ctx.author.send(f' | ID: ``{ret_id}``\n{cont}')
    #     await preview_msg.add_reaction('✅')
    #     await preview_msg.add_reaction('❌')
    #
    #     # Detect the verification
    #     def check(reaction, user):
    #         return (user == ctx.author and str(reaction.emoji) == '✅') or (user == ctx.author and str(reaction.emoji) == '❌')
    #
    #     try:
    #         reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    #     except asyncio.TimeoutError:
    #         await ctx.author.send(f'Previous preview has timed out. Return to {ac.mention}?')
    #         return
    #     else:
    #         if str(reaction.emoji) == '✅':
    #             await ctx.author.send(f'You can view your new post in {ac.mention}')
    #             await ac.send(f' | ID: ``{ret_id}``\n{cont}')
    #
    #         else:
    #             await ctx.author.send(f'Preview declined. Return to {ac.mention}?')


    @commands.command()
    async def progress(self, ctx, *, cont):

        # Check if the author is progress muted or not
        mute_role = discord.utils.get(self.bot.agdg.roles, id=426372445998546946)
        for role in ctx.author.roles:
            if role == mute_role:
                await ctx.message.add_reaction('❌')
                await ctx.author.send("You have been muted and cannot post to the progress channel.")
                return


        # Wait for half a second to ensure embeds are logged properly
        if not ctx.message.embeds and not ctx.message.attachments:
            await self.bot.wait_for('message_edit', timeout=2.0)

        # Ensure that there is either an embed, a link, or an attachment.
        num_attach = len(ctx.message.attachments)
        num_embed = len(ctx.message.embeds)
        print('Attachments: {}\tEmbeds: {}'.format(num_attach, num_embed))
        if num_attach < 1 and num_embed < 1:
            await ctx.message.add_reaction('❌')
            await ctx.author.send("Ensure that your progress post has attached media. Text-only posts are not allowed.")
            return
        if num_attach > 1 or num_attach > 1:
            # await ctx.message.add_reaction('❌')
            await ctx.author.send("Embeds will not be able to display more than one image.")

        prog_channel = ctx.guild.get_channel(self.bot.prog_chan_ID)
        # print('Identified progress channel.\tName:{0.name}\tID:{0.id}'.format(prog_channel))

        # Small shortcut
        msg = ctx.message

        # Construct the embed
        sig = '\n\n*Posted in* {0.channel.mention} *by* {0.author.mention}'.format(msg)
        emb = discord.Embed(color=msg.author.color, description=cont + sig, timestamp=msg.created_at)
        emb.set_author(name=str(msg.author.display_name), icon_url=msg.author.avatar_url)
        emb.set_footer(text='Originally posted in #{0.channel}'.format(msg), icon_url=ctx.guild.icon_url)

        # Determine which image to display
        # Simultaneously checks for special files such as .webms and .mp4
        sfile_url = None
        sfile_filename = None

        if msg.attachments:
            test_attach = msg.attachments[0]

            # 8MB is equal to 8388608 bytes in binary.
            # TODO: Remove this debug print and use it to check against filesize.

            if test_attach.url.endswith('.webm') or test_attach.url.endswith('.mp4'):
                # TODO: Add in a check for 8MB filesize here and if it is less, download and re-upload it.
                sfile_url = test_attach.url
                sfile_filename = test_attach.filename
            elif test_attach.width:
                emb.set_image(url=test_attach.url)
        elif msg.embeds:
            tar_embed = msg.embeds[0]
            if tar_embed:
                if tar_embed.url.endswith('.jpeg') or tar_embed.url.endswith('.jpg') or tar_embed.url.endswith('.gif') or tar_embed.url.endswith('.png'):
                    emb.set_image(url=tar_embed.url)
                else:
                    sfile_url = tar_embed.url

        # Send the preview to the User and have them verify it before posting
        verify_text = '**Wow, nice progress!**\nBelow is a preview of your progress post. To confirm or decline just ' \
                      'react with ✅ or ❌ and we\'ll do the rest. Keep up the good work!\n\n**Preview:**\n'
        verify_msg = await ctx.author.send(verify_text, embed=emb)
        if sfile_url is not None:
            second_msg = await ctx.author.send('Preview for: '+sfile_url)
            await second_msg.add_reaction('✅')
            await second_msg.add_reaction('❌')
        else:
            await verify_msg.add_reaction('✅')
            await verify_msg.add_reaction('❌')

        # Detect the verification
        def check(reaction, user):
            return (user == ctx.author and str(reaction.emoji) == '✅') or (user == ctx.author and str(reaction.emoji) == '❌')

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send('Previous preview has timed out. Return to {}?'.format(msg.channel.mention))
            return
        else:
            if str(reaction.emoji) == '✅':
                await ctx.author.send('Congratulations! You can view your new post in {} or return to {} and continue '
                                      'the discussion.'.format(prog_channel.mention, msg.channel.mention))
                await prog_channel.send(embed=emb)

                # If it was determined that a second message is needed, send  that too.
                if sfile_url is not None:
                    await prog_channel.send('Preview for: ' + sfile_url)

            else:
                await ctx.author.send('Preview declined. Return to {}?'.format(msg.channel.mention))


    @progress.error
    async def progress_error(ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.message.add_reaction('❌')
            await ctx.send("Ensure that your progress post contains text.")


    # TODO: Make this not a hacky piece of crap. Consider using a generated .txt file to bypass 2k character limit.
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def formatroles(ctx):
        await ctx.send(f'Displaying information for {len(ctx.guild.roles)} roles:')
        sorted_roles = sorted(ctx.guild.roles)

        chunk_size = int(math.ceil(math.sqrt(len(sorted_roles))))
        first_limit = 0
        second_limit = chunk_size
        while first_limit <= len(sorted_roles):
            list_chunk = []
            for i in sorted_roles[first_limit:second_limit]:
                list_chunk.append('{}\t{}\t{}\n'.format(i.position, i.name, i.id))
            await ctx.send(f'```{first_limit} to {second_limit}:\n{"".join(list_chunk)} ```')

            # Advance the limits to the next bracket
            first_limit += chunk_size
            second_limit += chunk_size
            if second_limit > len(sorted_roles):
                second_limit = len(sorted_roles)

def setup(bot):
    bot.add_cog(Core(bot))