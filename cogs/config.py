import discord
import asyncio
import datetime
import sqlite3
import os
from discord.ext import commands
from discord.utils import get
from .lib import check_block, get_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def has_moderator(ctx):
        for role in ctx.author.roles:
            if ctx.author.id == 344666116456710144 or role.permissions.administrator:
                return True
        return False

    async def not_blocked(ctx):
        return check_block(ctx.author.id, ctx.command.name)

    async def create_command_check(self, type, guild, type_id, ctx):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM command_check WHERE server_id=? and type=?", (guild.id, type,))

        row = c.fetchone()

        if row:
            c.execute("UPDATE command_check SET type_id=? WHERE server_id=? AND type=?", (type_id, guild.id, type,))
            conn.commit()
            conn.close()
            return

        default = get(guild.roles, name="@everyone")
        perms = default.permissions
        role = await guild.create_role(name=type, permissions=perms)


        c.execute("INSERT INTO command_check (type_id, server_id, type) VALUES (?,?,?)", (role.id, guild.id, type,))
        conn.commit()
        conn.close()


    @commands.group(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of set command")
            await asyncio.sleep(2)
            await msg.delete()

    @set.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def prefix(self, ctx, *, prefix):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("UPDATE servers SET prefix=? WHERE server_id=?", (prefix,ctx.guild.id,))
        conn.commit()

        await ctx.send(f"Your prefix has been set to `{prefix}`")

    @set.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def mute(self, ctx, role: discord.Role):
        await ctx.send("?")
        try:
            await get_id(ctx.guild, "Mute", role.id)
            await ctx.send(f"Set muted role to {role.mention}, make sure to adjust the perms!")
        except Exception as e:
            await ctx.send(e)

    @set.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def dungeon(self, ctx, role: discord.Role):
        await get_id(ctx.guild, "Dungeon", role.id)
        await ctx.send(f"Set dungeond role to {role.mention}, make sure to adjust the perms!")

    @set.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def moderator(self, ctx, role: discord.Role):
        try:
            await get_id(ctx.guild, "Moderator", role.id)
            await ctx.send(f"Added {role.mention} as a moderator")
        except Exception as e:
            await ctx.send(e)

    @set.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def admin(self, ctx, role: discord.Role):
        await get_id(ctx.guild, "Administrator", role.id)
        await ctx.send(f"Added {role.mention} as an Admin")





def setup(bot):
    bot.add_cog(ConfigCog(bot))
