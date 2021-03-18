from discord.ext import commands
import discord
import asyncio
import sqlite3
import os
import requests
from .classes.UserAccount import UserAccount
from discord.utils import get
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_user(self, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id=?", (id,))
        return c.fetchone()

    @commands.command("banrole")
    @commands.is_owner()
    async def banrole(self, ctx, roleId: int):
        role = dungoned = get(ctx.author.guild.roles, id=roleId)
        to_ban = role.members

        for member in to_ban:
            await member.ban()
            await ctx.send("Users with the {} role have been banned!".format(role.name))

    @commands.command("dungeonrole")
    @commands.is_owner()
    async def dungeonrole(self, ctx, roleId: int):
        role = get(ctx.author.guild.roles, id=roleId)
        to_dungeon = role.members

        dungoned = get(ctx.author.guild.roles, name="Dungeoned 🔗")
        for member in to_dungeon:
            await member.add_roles(dungoned, reason="reason", atomic=True)

        await ctx.send("Everyone with the role {} has been dungoned".format(role.name))

        dungeon = self.bot.get_channel(777217521429643277)
        await dungeon.send("Welcome to the dungeon {}".format(role.name))

    @commands.command("block")
    @commands.is_owner()
    async def block(self, ctx, id: int, command):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        await ctx.message.delete()
        c.execute("INSERT INTO blocked (user_id, command) VALUES (?,?)", (id,command,))
        conn.commit()

        await ctx.send("{} has been blocked from the {} command".format(self.bot.get_user(id).mention, command))
        return

    @commands.command("unblock")
    @commands.is_owner()
    async def unblock(self, ctx, id: int, command):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        await ctx.message.delete()
        c.execute("DELETE FROM blocked WHERE user_id=? AND command=?", (id,command,))
        conn.commit()

        await ctx.send("{} has been unblocked from the {} command".format(self.bot.get_user(id).mention, command))
        return


    @commands.command("releaserole")
    @commands.is_owner()
    async def realeaserole(self, ctx, roleId: int):
        role = get(ctx.author.guild.roles, id=roleId)
        to_release = role.members
        dungoned = get(ctx.author.guild.roles, name="Dungeoned 🔗")
        for member in to_release:
            await member.remove_roles(dungoned, reason = "released")

        await ctx.send("Everyone with the role {} has been released".format(role.name))

    @commands.command(name="database")
    @commands.is_owner()
    async def database(self, ctx):
        for guild in self.bot.guilds:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            c.execute("INSERT INTO servers (server_id, prefix) VALUES (?, ?)", (guild.id,'$',))
            conn.commit()

    @commands.command(name='shutdown', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        mike = ""
        obServer = self.bot.get_guild(737104128777650217)
        #I KNOW I CAN JUST GET THE EMOTE STRING SHUT UP  O_O
        for emoji in obServer.emojis:
            emojiName = emoji.name.replace("OB_", "")
            if emojiName.lower() == "mike":
                mike = str(emoji)
                break
        channel = self.bot.get_channel(774799606889447504)
        await channel.send("Arnold signing off, no shenanigans {}".format(mike))
        await self.bot.close()

    @commands.command(name='talk', hidden=True)
    @commands.is_owner()
    async def talk(self, ctx, channelId: int):
        channel = self.bot.get_channel(channelId)

        def check(m):
            return True

        while (True):
            m = await self.bot.wait_for('message', check=check)

            if m.author == ctx.author and m.channel == ctx.channel:
                if m.content == "$end":
                    return
                else:
                    await channel.send(m.content)

            if m.channel == channel:
                await ctx.send(f'{m.author}: {m.content}')


    @commands.command(name='colour', hidden=True)
    @commands.is_owner()
    async def colour(self, ctx, roleName, colour):
        try:
            role = get(ctx.guild.roles, name=roleName)
        except:
            await ctx.send("That role doesn't exist")
            return
        await role.edit(color=int(colour, 16))

    @commands.command(name='create', hidden=True)
    @commands.is_owner()
    async def create(self, ctx, name, colour):
        role = await ctx.guild.create_role(name=name)
        await role.edit(color=int(colour, 16))
        await ctx.send(f"Role {name} was created")
        return

    @commands.is_owner()
    @commands.group(pass_context=True)
    async def suggestions(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of casino command")
            await asyncio.sleep(2)
            await msg.delete()

    @suggestions.command(pass_context=True)
    @commands.is_owner()
    async def show(self, ctx, status):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE status=?", (status,))
        suggestions = c.fetchall()

        if suggestions:
            embed = discord.Embed(title="Suggestions", colour=0xc7e6a7, description=status)
            for suggestion in suggestions:
                embed.add_field(name="\u200b", value="{}: <@{}>\n{}".format(str(suggestion[0]), str(suggestion[1]), suggestion[2]))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No suggestions found")

    @suggestions.command(pass_context=True)
    @commands.is_owner()
    async def complete(self, ctx, id: int):
        await ctx.message.delete()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE id=?", (id,))
        suggestion = c.fetchone()

        if suggestion:
            c.execute("UPDATE suggestions SET status=? WHERE id=?", ("complete", id,))
            conn.commit()
            conn.close()

            await ctx.send("{} your suggestion of '{}' is complete!".format(self.bot.get_user(suggestion[1]).mention, suggestion[2]))
            return
        else:
            await ctx.send("Suggestion doesn't exist")

    @suggestions.command(pass_context=True)
    @commands.is_owner()
    async def delete(self, ctx, id: int):
        await ctx.message.delete()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE id=?", (id,))
        suggestion = c.fetchone()

        if suggestion:
            c.execute("DELETE FROM suggestions WHERE id=?", (id,))
            conn.commit()
            conn.close()

            await ctx.send("{} your suggestion of '{}' was deleted! <:OB_mike:737105902720647258>".format(self.bot.get_user(suggestion[1]).mention, suggestion[2]))
            return
        else:
            await ctx.send("Suggestion doesn't exist")

    @commands.is_owner()
    @commands.group(pass_context=True)
    async def dev(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of dev command")
            await asyncio.sleep(2)
            await msg.delete()

    @dev.group(pass_context=True)
    async def reload(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of reload command")
            await asyncio.sleep(2)
            await msg.delete()

    @reload.command(pass_context=True)
    async def users(self, ctx):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            c.execute("DELETE $FROM users")
            conn.commit()

            for guild in self.bot.guilds:
                for member in guild.members:
                    c.execute("INSERT INTO users (user_id, balance, score, pomodoro) VALUES (?,?,?,?)", (member.id, 1000, 0, 0,))
            conn.commit()
            await ctx.send("Done!")
        except Exception as e:
            await ctx.send(e)

    @dev.group(pass_context=True)
    async def give(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of give command")
            await asyncio.sleep(2)
            await msg.delete()

    @give.command(pass_context=True)
    async def stock(self, ctx, stock, shares: int, user: discord.Member):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO portfolio (ticker, shares, user_id) VALUES (?,?,?)", (stock, shares, user.id,))
        conn.commit()
        await ctx.send("Done!")

    @give.command(pass_context=True)
    async def money(self, ctx, amount: int, user: discord.Member):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user.id,))
        conn.commit()
        await ctx.send("Done!")

    @dev.command(pass_context=True, name="expropriate", aliases=["ex"])
    async def expropriate(self, ctx, user: discord.Member, amount: int):
        reciever = UserAccount(ctx.author.id)
        sender = UserAccount(user.id)
        if (sender.get_balance()) >= amount:
            sender.change_money(amount, "remove")
            reciever.change_money(amount, "add")
            await ctx.send(f"You expropriated {amount} from {user.name}")
        else:
            await ctx.send("They don't have {}".format(amount))


def setup(bot):
    bot.add_cog(OwnerCog(bot))
