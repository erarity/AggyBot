import discord
import json
import asyncio
import io
from discord.ext import commands

bot = commands.Bot(command_prefix='>')

# react_timer = 7

# Obtain the token
with open('token.json') as token_file:
    token_data = json.load(token_file)
token = token_data["token"]

# Obtain the role ids.
with open('roles.json') as role_file:
    role_data = json.load(role_file)

prisonerID = role_data["prisoner"]
colorsID = role_data["colors"]
skillsID = role_data["skills"]
modID = role_data["moderator"]

admin_chan_ID = role_data["admin"]
log_chan_ID = role_data["botlog"]
prog_chan_ID = role_data["progress"]

@bot.event
async def on_ready():
    print('Bot ready!')
    print('Logged in as {0.user.name}'.format(bot))
    print('----------')
    # game = discord.Game(name='your shitty games.')
    # await bot.change_presence(game=None)

    # Obtain the guild
    agdg = bot.get_guild(121565307515961346)
    print('Targeted guild is {0.name}'.format(agdg))

    # Fetch channel objects
    admin_channel = discord.utils.get(agdg.channels, id=admin_chan_ID)
    print('Identified admin channel.\tName:{0.name}\tID:{0.id}'.format(admin_channel))

    log_channel = discord.utils.get(agdg.channels, id=log_chan_ID)
    print('Identified log channel.\tName:{0.name}\tID:{0.id}'.format(log_channel))


@bot.event
async def on_member_remove(mem):
    for role in mem.roles:
        if role.id == prisonerID:
            print("A user left the server with the prisoner role.")


@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.BadArgument):
        await ctx.send('No Dice. Try: ``' + ctx.command.signature + '``')


# @bot.command()
# @commands.has_permissions(manage_roles=True)
# async def showroles(ctx):
#     await ctx.send('displaying all roles')
#     sorted_roles = sorted(ctx.guild.roles)
#     for i in sorted_roles:
#         await ctx.send('{}\t{}\t{}'.format(i.position, i.name, i.id))


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


@bot.command()
async def color(ctx, col):
    # await ctx.send('Assigning color.')
    colors = discord.utils.get(ctx.guild.roles, id=colorsID)
    skills = discord.utils.get(ctx.guild.roles, id=skillsID)
    # await ctx.send('positions are c{} and s{}'.format(colors.position, skills.position))

    # Sort the list.
    sorted_roles = sorted(ctx.guild.roles)

    # Iterate through the sublist
    for c in sorted_roles[skills.position + 1: colors.position]:

        if c.name.lower() == col.lower():
            await ctx.author.add_roles(c)

            # Members can only have one color, so check if they already have a color role and replace it.
            for i in sorted_roles[skills.position + 1: colors.position]:
                if i in ctx.author.roles and i != c:
                    await ctx.author.remove_roles(i)

            await ctx.message.add_reaction('✅')
            return

    await ctx.message.add_reaction('❌')


@bot.command()
async def addskill(ctx, skill):
    # await ctx.channel.send('Adding skill')
    skills = discord.utils.get(ctx.guild.roles, id=226331683996172288)

    # Iterate through the sublist
    sorted_roles = sorted(ctx.guild.roles)
    for s in sorted_roles[:skills.position]:
        if s.name.lower() == skill.lower():
            await ctx.author.add_roles(s)
            await ctx.message.add_reaction('✅')
            return
    await ctx.message.add_reaction('❌')


@bot.command()
async def removeskill(ctx, skill):
    # await ctx.channel.send('Removing skill')
    # target_role = discord.utils.get(ctx.guild.roles, name=skill)
    skills = discord.utils.get(ctx.guild.roles, id=226331683996172288)

    sorted_roles = sorted(ctx.guild.roles)
    for s in sorted_roles[:skills.position]:
        if s.name.lower() == skill.lower():
            await ctx.author.remove_roles(s)
            await ctx.message.add_reaction('✅')
            return
    await ctx.message.add_reaction('❌')
    # await asyncio.sleep(react_timer)
    # await ctx.message.remove_reaction('✅', ctx.guild.me)


@bot.command()
@commands.has_permissions(kick_members=True)
async def jail(ctx, member: discord.Member, time: int=30, *, reason=None):
    # await ctx.channel.send('Jailing {}'.format(member.display_name))
    jail_role = discord.utils.get(ctx.guild.roles, id=367155287343366144)
    mod_role = discord.utils.get(ctx.guild.roles, id=121566377063481344)

    if not member.top_role >= mod_role:

        await member.add_roles(jail_role)

        # Determine if the reason needs to be tacked on
        if reason is not None:
            full_reason = ' Reason: {}'.format(reason)
        else:
            full_reason = ''

        # TODO: Log the jailing to the audit log and json file.

        # Send out notifications on all appropriate channels.
        ctx.send('**{} was jailed for {} minutes.**'.format(member.display_name, time) + full_reason)

        # Wait the determined amount of time before removing the role.
        await asyncio.sleep(float(time*60))
        await member.remove_roles(jail_role)


@bot.command()
@commands.has_permissions(kick_members=True)
async def unjail(ctx, member: discord.Member):
    await ctx.channel.send('Un-Jailing {}'.format(member.display_name))
    jail_role = discord.utils.get(ctx.guild.roles, id=367155287343366144)
    await member.remove_roles(jail_role)


@bot.command()
async def checkrole(ctx, *, arg1):
    for role in ctx.guild.roles:
        if role.name.lower() == arg1.lower():
            await ctx.channel.send('There are {} users with the {} role.'.format(len(role.members), role.name))


@bot.command()
@commands.has_permissions(kick_members=True)
async def progress(ctx, *, cont):

    # Ensure that there is either an embed, a link, or an attachment.
    num_attach = len(ctx.message.attachments)
    num_embed = len(ctx.message.embeds)
    if num_attach < 1:
        print("Number of attachments is 0.")
    if num_embed < 1:
        print("Number of embeds is 0.")

    prog_channel = discord.utils.get(ctx.guild.channels, id=prog_chan_ID)
    print('Identified progress channel.\tName:{0.name}\tID:{0.id}'.format(prog_channel))

    msg = ctx.message

    # Handle attachments
    file_list = []
    for attach in msg.attachments:
        b = io.BytesIO()
        attach.save(b)
        b.seek(0)
        f = discord.File(b, attach.filename)
        file_list.append(f)

    print(file_list)

    await prog_channel.send(content='``Channel:`` {0.channel.mention}\t``Author:`` {0.author.mention}\n'.format(msg) +
                                    cont, files=file_list)
    print("done")

bot.run(token)
