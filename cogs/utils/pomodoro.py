from discord.ext import commands
import discord
import asyncio

class Pomodoro(commands.Cog):
    """"""

    def __init__(self, bot):
        self.bot = bot
        self.pomo_role = discord.utils.get(bot.agdg.roles, id=367155287343366144)

    @commands.group(pass_context=True)
    async def slampomo(self, ctx, time: int = 25):
        if not isinstance(time, int):
            await ctx.message.add_reaction('❌')
            await ctx.send('Enter a valid time in minutes (10-1440).')
            return
        if time > 1440:
            await ctx.message.add_reaction('❌')
            await ctx.send('Ensure maximum time is less than a day (1440 minutes).')
            return
        if time < 10:
            await ctx.message.add_reaction('❌')
            await ctx.send("Ensure minimum time is at least 10 minutes.")
            return

        #At this point, input should be good so add the role.
        mem = self.bot.agdg.get_member(ctx.author.id)
        if mem is not None:
            await mem.add_roles(self.pomo_role)
            await ctx.message.add_reaction('✅')