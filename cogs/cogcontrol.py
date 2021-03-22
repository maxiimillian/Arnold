from discord.ext import commands
import discord
import asyncio
import os
from discord.utils import get
from discord.ext import commands
from discord.utils import get

class CogControl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_user(self, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id=?", (id,))
        return c.fetchone()

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def _cog_load(self, ctx, *, cog: str):
        #loads a cog
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def _cog_unload(self, ctx, *, cog: str):
        #unloads a cog
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _cog_reload(self, ctx, *, cog: str):
        #reloads a cog
        await ctx.send(cog)
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reset', hidden=True)
    @commands.is_owner()
    async def _cog_reset(self, ctx):
        #reloads a cog
        failed = []
        ignore_list = ["lib.py"]

        try:
            for file in os.listdir("/home/pi/Arnold/cogs"):
                try:
                    if file.endswith(".py") and file not in ignore_list:
                        self.bot.unload_extension(cog)
                        self.bot.load_extension(f'cogs.{file[:-3]}')
                        print("Loaded: {}".format(file))
                except:
                    failed.append(file)
            await ctx.send(f"Done: These cogs failed to reload: {failed}")
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')



def setup(bot):
    bot.add_cog(CogControl(bot))
