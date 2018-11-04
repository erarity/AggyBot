from discord.ext import commands
import discord
import asyncio
# from checks import mod_or_permissions, is_owner
import json


class RoleKeeper:
    """"""

    def __init__(self, bot):
        # TODO: Change the names on the JSON values?
        with open('roles.json') as json_file:
            json_data = json.load(json_file)
        self.bot = bot
        self.json_data = json_data
        self.saved_roles = json_data["saved_roles"]
        self.role_dict = json_data["roleme_roles"]

    async def on_member_remove(self, member):
        if member.nick is None or member.nick == member.display_name and not member.roles or \
                                member.nick == member.display_name and len(member.roles) == 1:
            return

        self.json_data['members'][member.id] = dict(roles=[x.id for x in member.roles if x.id in self.saved_roles],
                                                    nickname='None' if member.nick is None else member.nick,
                                                    name=member.display_name)

        with open('roles.json', 'w') as json_file:
            json_file.write(json.dumps(self.json_data, indent=2))

    async def on_member_join(self, member):
        try:
            member_json = self.json_data['members'].pop(member.id)

            role_list = [discord.Object(id=r_id) for r_id in member_json['roles']]
            await self.bot.add_roles(member, *role_list)

            # Reassign their nickname on file.
            # TODO: Consider removing this?
            try:
                if member_json['nickname'] != 'None':
                    await self.bot.change_nickname(member, member_json['nickname'])
            except discord.Forbidden:
                pass

            with open('roles.json', 'w') as json_file:
                json_file.write(json.dumps(self.json_data, indent=2))

        except KeyError:
            pass

    @commands.group(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def rolekeep(self, ctx):
        """The commands group for adding and removing "sticky" roles - or roles that are kept on server join/leave"""
        pass

    @rolekeep.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, *, role_name: str):
        """The command to add roles to the sticky role list"""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is not None:
            if role.id not in self.saved_roles:
                self.json_data['saved_roles'].append(role.id)
                self.saved_roles = self.json_data["saved_roles"]
                with open('roles.json', 'w') as json_file:
                    json_file.write(json.dumps(self.json_data, indent=2))
                await ctx.send(f'Added {role_name} to the list of sticky roles!')
            else:
                await ctx.send(f'{role_name} is already a sticky role.')
        else:
            await ctx.send('Unable to find a role by that name.')

    @rolekeep.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, *, role_name: str):
        """The command to remove roles from the sticky role list"""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is not None:
            if role.id in self.saved_roles:
                self.json_data['saved_roles'].remove(role.id)
                self.saved_roles = self.json_data['saved_roles']
                with open('roles.json', 'w') as json_file:
                    json_file.write(json.dumps(self.json_data, indent=2))
                await ctx.send(f'Removed {role_name} from the list of sticky roles!')
            else:
                await ctx.send(f'{role_name} is already a sticky role.')
        else:
            await ctx.send('Unable to find a role by that name.')

    @rolekeep.command(pass_context=True, name='list')
    @commands.has_permissions(manage_roles=True)
    async def _list(self, ctx):
        """Lists all the sticky roles"""
        role_list = [x.name for x in ctx.guild.roles if x.id in self.saved_roles]
        await ctx.send('The following roles are sticky:\n ```{}```'.format('\n'.join(role_list)))

    # TODO: REMEMBER: Ctrl + / to comment a block of code.

    # @commands.group(pass_context=True, aliases=['roles'], invoke_without_command=True)
    # @commands.cooldown(1, 3600, commands.BucketType.user)
    # async def role(self, ctx, *, role_name: str = None):
    #     try:
    #         if role_name is None:
    #             await ctx.send('The following are valid autoRoles:\n```{}```'.format(
    #                 '\n'.join([x.title() for x in self.role_dict.keys()])))
    #             ctx.cooldown.reset()
    #             return
    #         if role_name.lower() not in self.role_dict.keys() and role_name.lower() != 'remove':
    #             await ctx.send(f'{role_name} is not a valid autoRole.')
    #             ctx.cooldown.reset()
    #             return
    #         role_replacement = [discord.Object(id=x.id) for x in ctx.author.roles
    #                             if x.id not in self.role_dict.values()]
    #         if role_name.lower() != 'remove':
    #             role_replacement.append(discord.Object(id=self.role_dict[role_name.lower()]))
    #         else:
    #             ctx.cooldown.reset()
    #         await self.bot.replace_roles(ctx.author, *role_replacement)
    #         await self.bot.add_reaction(ctx.message, '✅')
    #         await asyncio.sleep(5)
    #         # Todo: Bot deletes message. Consider removing.
    #         await self.bot.delete_message(ctx.message)
    #     except discord.Forbidden as e:
    #         await self.bot.log_channel.send(f'<@143454150636732416>: {e}')
    #
    # @role.command(pass_context=True)
    # async def list(self, ctx):
    #     await ctx.send('The following are valid autoRoles:\n```{}```'.format(
    #         '\n'.join([x.title() for x in self.role_dict.keys()])))
    #
    # @role.command(pass_context=True)
    # @commands.has_permissions(manage_roles=True)
    # async def admin_add(self, ctx, *, role_name):
    #     """Adds a role to the possible autoroles"""
    #     role_obj = discord.utils.get(ctx.message.server.roles, name=role_name)
    #     if role_obj is None:
    #         await ctx.send(f'Unable to find a role by name {role_name}')
    #     else:
    #         role_name = role_name.lower()
    #         if role_name in self.role_dict.keys():
    #             await ctx.send('This is already a roleme role.')
    #             return
    #         self.json_data['roleme_roles'][role_name] = role_obj.id
    #         with open('roles.json', 'w') as json_file:
    #             json_file.write(json.dumps(self.json_data, indent=2))
    #         await ctx.send(f'Added {role_name} to the list of roleme roles.')
    #
    # @role.command(pass_context=True)
    # @commands.has_permissions(manage_roles=True)
    # async def admin_remove(self, ctx, *, role_name):
    #     """Adds a role to the possible autoroles"""
    #     role_obj = discord.utils.get(ctx.guild.roles, name=role_name)
    #     if role_obj is None:
    #         await self.bot.say(f'Unable to find a role by name {role_name}')
    #     else:
    #         role_name = role_name.lower()
    #         if role_name not in self.role_dict.keys():
    #             await ctx.send('This is not a roleme role.')
    #             return
    #         self.json_data['roleme_roles'].pop(role_name)
    #         with open('roles.json', 'w') as json_file:
    #             json_file.write(json.dumps(self.json_data, indent=2))
    #         await ctx.send(f'Removed {role_name} from the list of roleme roles.')
    #
    # @role.error
    # async def role_error(self, error, ctx):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         delete_message = await self.bot.log_channel.send(error)
    #         await asyncio.sleep(5)
    #         # await self.bot.delete_message(delete_message)
    #         # TODO: Consider toggling the removal of messages.
    #         await self.bot.delete_message(ctx)
    #     else:
    #         print(error)


def setup(bot):
    bot.add_cog(RoleKeeper(bot))
