from discord.ext import commands


class OwnerCog:

    def __init__(self, bot):
        self.bot = bot

    # Won't show up on default help command.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog:str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`SUCCESS`**')

    @commands.command(name='listcogs', hidden=True)
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """Command which Lists all Modules."""
        await ctx.send('Installed Cogs:\n```{}```'.format('\n'.join(x for x in self.bot.cogs)))


def setup(bot):
    bot.add_cog(OwnerCog(bot))
