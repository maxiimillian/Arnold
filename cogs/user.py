#Commands for every user
#ToDo: Change all of the database entries into something using the user class
import discord
import asyncio
import time
import random
import sqlite3
import os.path
import wikipediaapi
import json
import praw
import math
from PyPDF2 import PdfFileReader
from .lib import check_block, get_value, get_id
from .classes.UserAccount import UserAccount
from discord.utils import get

from discord.ext import commands

#Gets the absolute path to the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def not_blocked(ctx):
        return check_block(ctx.author.id, ctx.command.name)

    async def is_librarian(ctx):
        return ctx.author.id == 344666116456710144 or ctx.author.id == 411930339523428364

    def to_lower(arg):
        return arg.lower()

    @commands.command(name="ob")
    @commands.check(not_blocked)
    async def ob(self, ctx, *, names):
        #This is a personal emote server
        obServer = self.bot.get_guild(737104128777650217)
        names = names.split()
        response = ""
        for name in names:
            for emoji in obServer.emojis:
                emojiName = emoji.name.replace("OB_", "")
                if emojiName.lower() == name.lower():
                    response = response + " " + str(emoji)
        await ctx.send(response)
        await ctx.message.delete()

    @commands.command(name="remindme", aliases=["rm", "remind"])
    @commands.check(not_blocked)
    async def remindme(self, ctx, amount: int, unit: str, *, reminder: str):
        to_seconds = {"second": 1, "minute": 60, "hour": 3600, "day": 86400, "week": 604800, "month": 2592000}
        unit = unit.lower()

        if unit.endswith('s'):
            unit = unit[:-1]
        if not unit in to_seconds:
            await ctx.send("Unit must be seconds/minutes/hours/days/weeks/months")
            return
        if amount < 1:
            await ctx.send("Amount must be greater than 0")
            return
        if len(reminder) > 1960:
            await ctx.send("Reminder text is too long")
            return

        time_in_seconds = to_seconds[unit] * amount
        remind_time = int(time.time()+time_in_seconds)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO reminders (user_id, time, reminder, channel_id) VALUES (?,?,?,?)", (ctx.author.id, remind_time, reminder, ctx.channel.id,))
        conn.commit()
        conn.close()

        await ctx.send("Reminder set!")
        return

    @commands.group(pass_context=True)
    @commands.check(not_blocked)
    async def todo(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of todo command")
            await asyncio.sleep(2)
            await msg.delete()

    @todo.command(pass_context=True, name="add")
    @commands.check(not_blocked)
    async def todoadd(self, ctx, *, item):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if len(item) > 200:
            await ctx.send("Item name is too long")
            return

        c.execute("INSERT INTO todo (user_id, item) VALUES (?,?)", (ctx.author.id, item,))
        conn.commit()
        conn.close()

        await ctx.send("Added to your ToDo List!")
        return

    @todo.command(pass_context=True, name="show", aliases=["list"])
    @commands.check(not_blocked)
    async def todoshow(self, ctx):
        try:
            user = UserAccount(ctx.author.id)
            todo_list = user.get_todo()
            loop_count = 0
            page_count = 0
            text = ""
            pages = []

            if not todo_list:
                await ctx.send("You have nothing on your list")
                return

            for todo_item in todo_list:
                #text = text + f"{loopCount+1}: {todo_item[0]}"
                if todo_item[2] == "crossed":
                    text = text + f"\n~~{todo_item[1]}: {todo_item[0]}~~"
                else:
                    text = text + f"\n{todo_item[1]}: {todo_item[0]}"

                loop_count += 1
                if loop_count % 10 == 0 or loop_count-1 == len(todo_list)-1:
                    embed = discord.Embed(colour=0xc7e6a7)

                    embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
                    embed.add_field(name="\u200b",value=text, inline=False)
                    embed.set_footer(text=f"Page {len(pages)}/{math.floor(len(todo_list)/10)} ({len(todo_list)} items)")

                    pages.append(embed)
                    text = ""

            embed_msg = await ctx.send(embed=pages[page_count])
            await embed_msg.add_reaction("◀️")
            await embed_msg.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and reaction.message == embed_msg

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await embed_msg.clear_reaction("◀️")
                    await embed_msg.clear_reaction("▶️")
                    return
                else:
                    if str(reaction) == "▶️":
                        try:
                            await embed_msg.edit(embed=pages[page_count+1])
                        except:
                            continue
                        page_count += 1
                    elif str(reaction) == "◀️":
                        try:
                            await embed_msg.edit(embed=pages[page_count-1])
                        except:
                            continue
                        page_count -= 1

        except Exception as e:
            await ctx.send(e)

    @todo.command(pass_context=True, name="remove")
    @commands.check(not_blocked)
    async def todoremove(self, ctx, id: int=None):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()


            c.execute("DELETE FROM todo WHERE id=? AND user_id=?", (id, ctx.author.id,))
            conn.commit()
            conn.close()

            await ctx.send("It's deleted!")
            return
        except Exception as e:
            await ctx.send(e)

    @todo.command(pass_context=True)
    @commands.check(not_blocked)
    async def cross(self, ctx, id: int):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()


            c.execute("UPDATE todo SET status=? WHERE id=? AND user_id=?", ("crossed", id, ctx.author.id,))
            conn.commit()
            conn.close()

            await ctx.send("It's crossed out!")
            return
        except Exception as e:
            await ctx.send(e)

    @todo.command(pass_context=True)
    @commands.check(not_blocked)
    async def uncross(self, ctx, id: int):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()


            c.execute("UPDATE todo SET status=? WHERE id=? AND user_id=?", ("uncrossed", id, ctx.author.id,))
            conn.commit()
            conn.close()

            await ctx.send("It's uncrossed!")
            return
        except Exception as e:
            await ctx.send(e)

    @commands.group(pass_context=True)
    @commands.check(not_blocked)
    async def lib(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of lib command")
            await asyncio.sleep(2)
            await msg.delete()

    @lib.command(pass_context=True)
    @commands.check(not_blocked)
    @commands.check(is_librarian)
    async def add(self, ctx, isbn, *, title):
        path = os.path.abspath("Arnold/cogs/files/")
        try:
            files = ctx.message.attachments
            if not files:
                await ctx.send("You must have a pdf attachment")
                return
            if len(files) > 1 or files[0].size > 5000000 or not files[0].filename.endswith((".pdf", ".epub", ".mobi")):
                await ctx.send("You must have a single pdf less than 2mb")
                return

            await files[0].save(f"{path}/{files[0].filename}")

            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            c.execute("INSERT INTO books (isbn, title, filename) VALUES (?,?,?)", (isbn, title, files[0].filename,))
            conn.commit()

            await ctx.send("It's been added!")
        except Exception as e:
            await ctx.send(e)

    @lib.command(pass_context=True)
    @commands.check(not_blocked)
    async def get(self, ctx, *, query):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM books WHERE isbn=? or title=?", (query, query,))
        row = c.fetchone()

        if not row:
            await ctx.send("Can't find that in my library")
            return

        path = os.path.abspath(f"Arnold/cogs/files/{row[3]}")

        with open(path, "rb") as file:
            await ctx.send("Heres your file: ", file=discord.File(file, row[3]))

    @lib.command(pass_context=True)
    @commands.check(not_blocked)
    async def show(self, ctx):
        try:
            loop_count = 0
            page_count = 0
            text = ""
            pages = []

            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            c.execute("SELECT * FROM books")
            book_list = c.fetchall()

            if not book_list:
                await ctx.send("The library is empty :(")
                return

            for book in book_list:

                text = text + f"\n`{book[2]}`"

                loop_count += 1
                if loop_count % 10 == 0 or loop_count-1 == len(book_list)-1:
                    embed = discord.Embed(colour=0xc7e6a7, title="The Library")

                    embed.add_field(name="\u200b",value=text, inline=False)
                    embed.set_footer(text=f"Page {len(pages)}/{math.floor(len(book_list)/10)} ({len(book_list)} items)")

                    pages.append(embed)
                    text = ""

            embed_msg = await ctx.send(embed=pages[page_count])
            await embed_msg.add_reaction("◀️")
            await embed_msg.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and reaction.message == embed_msg

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await embed_msg.clear_reaction("◀️")
                    await embed_msg.clear_reaction("▶️")
                    return
                else:
                    if str(reaction) == "▶️":
                        try:
                            await embed_msg.edit(embed=pages[page_count+1])
                        except:
                            continue
                        page_count += 1
                    elif str(reaction) == "◀️":
                        try:
                            await embed_msg.edit(embed=pages[page_count-1])
                        except:
                            continue
                        page_count -= 1

        except Exception as e:
            await ctx.send(e)



    @commands.command(name="pomodoro")
    @commands.check(not_blocked)
    async def pomodoro(self, ctx, cycles: int):
        try:
            user = UserAccount(ctx.author.id)
            for x in range(cycles):
                breakTime = 0
                sleepTime = 0

                role_id = await get_id(ctx.guild, "Pomodoro")
                role = get(ctx.author.guild.roles, id=role_id)

                user.add_pomodoro(1)

                await ctx.send(f"{ctx.author.mention} Starting Cycle {x+1}")
                await asyncio.sleep(60*25)

                if (x+1) % 4 == 0:
                    breakTime = 60*25
                    await ctx.send(f"{ctx.author.mention} Starting Break (25 Minutes)")
                else:
                    breakTime = 60*5
                    await ctx.send(f"{ctx.author.mention} Starting Break (5 Minutes)")

                await asyncio.sleep(breakTime)

            await ctx.author.remove_roles(role, reason="Pomodoro Over", atomic=True)
            await ctx.send(f"{ctx.author.mention} your Pomodoro is over! You now have a score of {user.get_pomodoro()}")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="github")
    @commands.check(not_blocked)
    async def github(self, ctx):
        await ctx.send("https://github.com/Wenis77/Arnold")

    @commands.command(name="wiki")
    @commands.check(not_blocked)
    async def wiki(self, ctx, *, search):
        loopCount = 0
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(search)

        if not page.exists():
            await ctx.send("Page doesn't exist")
            return

        #If there are more than one wiki articles for a topic then give 8 options
        if len(page.sections) > 1:
            embed = discord.Embed(name='Sections', description="Pick one of these sections", colour=0xc7e6a7)
            for s in page.sections:
                if loopCount > 8: break;
                embed.add_field(name=str(loopCount), value=s.title, inline=False)
                loopCount+=1

            await ctx.send(embed=embed)

            #Recieving the section number from the author
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20.0)
            except asyncio.TimeoutError:
                return
            else:
                try:
                    section = page.sections[int(msg.content)]
                    embed = discord.Embed(name=section.title, colour=0xc7e6a7)
                    embed.add_field(name="Results: ", value=section.text[0:400] + "...")

                    await ctx.send(embed=embed)
                except Exception as e:
                    print("ERR: ", e)
                    await ctx.send("Your answer was invalid ")
        else:

            embed = discord.Embed(title=search.capitalize(), colour=0xc7e6a7)
            embed.add_field(name="Results:", value=page.summary[0:400] + "...")

            await ctx.send(embed=embed)

    @commands.command(name="meme")
    @commands.check(not_blocked)
    async def meme(self, ctx):
        #Retrive api info (hidden)
        secret = get_value("reddit-secret")
        id = get_value("reddit-personal")

        reddit = praw.Reddit(client_id=id, client_secret=secret, user_agent="Retrieves top posts from meme subreddits")

        meme = reddit.subreddit("dankmemes").random()

        embed = discord.Embed(title=meme.title, url="https://reddit.com{}".format(meme.permalink), colour=0xc7e6a7)
        embed.set_image(url=meme.url)
        await ctx.send(embed=embed)

        return


    #Currently bans but might be better to risk money or a mute
    @commands.command(name="roulette")
    @commands.check(not_blocked)
    async def roulette(self, ctx):
        roll = random.randint(1, 6)
        if roll == 3:
            await ctx.send("{} has been shot!".format(ctx.author.mention))
            await ctx.author.ban(delete_message_days=0)

        else:
            await ctx.send("You're safe!")

    @commands.command(name="leaderboard")
    @commands.check(not_blocked)
    async def leaderboard(self, ctx, type):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        loopCheck = 0

        try:
            c.execute("SELECT user_id, {} FROM users ORDER BY {} DESC".format(type, type))
            top = c.fetchall()

            embed = discord.Embed(title="Leaderboard for {}".format(type))
            for user in top:
                if loopCheck == 5: break;
                searchUser = self.bot.get_user(user[0])
                if not searchUser in ctx.guild.members: continue;
                embed.add_field(name=f"#{loopCheck+1}: {self.bot.get_user(user[0]).name}", value=f"Amount: {user[1]}", inline=False)
                loopCheck += 1

            await ctx.send(embed=embed)
        except sqlite3.OperationalError:
            await ctx.send("There is no leaderboard for that type")

    @commands.command(name="suggest")
    @commands.check(not_blocked)
    async def suggestion(self, ctx, *, suggestion):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO suggestions (user_id, suggestion, status) VALUES (?, ?, ?)", (ctx.author.id, suggestion, "incomplete"))
        conn.commit()

        await ctx.send("Your suggestion has been dumped in the trash!")

    @commands.command(name="fortune")
    @commands.check(not_blocked)
    async def fortune(self, ctx):
        #Just an array of fortuntes as a string
        with open("imports.json", 'r') as f:
            json_data = json.load(f)
            fortunes = json_data["fortunes"]
            await ctx.send(random.choice(fortunes))

def setup(bot):
    bot.add_cog(UserCog(bot))
