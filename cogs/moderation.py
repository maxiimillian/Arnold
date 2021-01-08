import discord
import asyncio
import datetime
import sqlite3
import os
from discord.ext import commands
from discord.utils import get

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_log(self, moderator: discord.Member, user: discord.Member, command, reason):
        image = user.avatar_url
        embed = discord.Embed(title=command, timestamp=datetime.datetime.now(), color=0x2403fc)
        embed.set_thumbnail(url=image)
        embed.add_field(name="Moderator", value=moderator, inline=True)
        embed.add_field(name="User", value=user, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)


        channel = self.bot.get_channel(789724879809019904)
        await channel.send(embed=embed)



    def get_length(self, textTime):
        textTime = textTime.lower()
        milliseconds = 0

        if textTime.find("d") != -1:
            intTime = textTime.replace("d","")
            intTime = int(intTime)
            milliseconds = 86400 * (int(intTime))

        elif textTime.find("h") != -1:
            intTime = textTime.replace("h","")
            intTime = int(intTime)
            milliseconds = milliseconds + 3600 * (int(intTime))

        elif textTime.find("m") != -1:
            intTime = textTime.replace("m","")
            intTime = int(intTime)
            milliseconds = 60  * (intTime)

        return milliseconds

    async def has_moderator(ctx):
        for role in ctx.author.roles:
            if role.id == 779430696510160936  or ctx.author.id == 344666116456710144:
                return True
        return False


    @commands.command(name="mute")
    @commands.check(has_moderator)
    async def mute(self, ctx, member: discord.Member, length, *, reason):
        print(member, length, reason)
        if member and length and reason:

            role = get(member.guild.roles, name="Muted 🔗")
            await member.add_roles(role, reason=reason, atomic=True)

            await ctx.message.delete()
            await ctx.send("{} has been muted for {}".format(member.mention, length))
            await self.create_log(ctx.author, member, ctx.command.name, reason)

            await asyncio.sleep(self.get_length(length))

            await member.remove_roles(role, reason = "time's up ")

        else:
            ctx.send("The command is `$mute *user* *length* *reason*`")


    @commands.command(name="unmute")
    @commands.check(has_moderator)
    async def unmute(self, ctx, member: discord.Member):

        if member:
            role = get(member.guild.roles, name="Muted 🔗")
            await member.remove_roles(role, reason = "time's up ")

            await self.create_log(ctx.author, member, ctx.command.name, None)
            await ctx.send("<@{}> has been unmuted!".format(member.id))
        else:
            ctx.send("The command is `$mute *user* *length* *reason*`")

    @commands.command(name="ban")
    @commands.check(has_moderator)
    async def ban(self, ctx, member: discord.Member, *, reason):
        if member.id == 344666116456710144:
            await ctx.send("you cant ban my master <:OB_pogO:737105405976772680>")
            return
        await ctx.send("DRUMROLLLLL PLEASE.... <@{}> is being banned!".format(member.id))
        await ctx.send("Banning <@{}> in: ".format(member.id))
        for x in reversed(range(1, 6)):
            await asyncio.sleep(1)
            await ctx.send(str(x))
        await member.ban(reason=reason)
        await ctx.send("<a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989> {} is banned! <a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989>".format(member.name))
        await self.create_log(ctx.author, member, ctx.command.name, reason)

    @commands.command(name="dungeon")
    @commands.check(has_moderator)
    async def dungeon(self, ctx, member: discord.Member, *, reason):

        if member and reason:
            role = get(member.guild.roles, name="Dungeoned 🔗")
            await member.add_roles(role, reason=reason, atomic=True)

            await ctx.message.delete()
            await ctx.send("{} has been dungeoned".format(member.mention))
            await self.create_log(ctx.author, member, ctx.command.name, reason)

            dungeon = self.bot.get_channel(777217521429643277)
            await dungeon.send("Welcome to the dungeon <@{}>, say hello to <@776124513866874920> <:OB_toph:776534087086768128>".format(member.id))
        else:
            ctx.send("The command is `$dungeon *user* *reason*`")

    @commands.command(name="release")
    @commands.check(has_moderator)
    async def release(self, ctx, member: discord.Member):

        if member:
            role = get(member.guild.roles, name="Dungeoned 🔗")
            await member.remove_roles(role, reason = "released")
            await self.create_log(ctx.author, member, ctx.command.name, None)

            await ctx.send("<@{}> has been released!".format(member.id))
        else:
            ctx.send("The command is `$release *user*`")

def setup(bot):
    bot.add_cog(ModerationCog(bot))