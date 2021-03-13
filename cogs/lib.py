from .classes.UserAccount import UserAccount
from discord.utils import get
import json
import asyncio
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")


"""Checks if a user can use a command"""
def check_block(id: int, command):
    print("id: {} Command: {}".format(id, command))
    user = UserAccount(int(id))

    for blocked_command in user.blocked_commands():
        print(blocked_command[0])
        if command == blocked_command[0]:
            return False
    else:
        return True

"""
Checks if an int is greater than zero, not negative, etc.
Essentially checks to make sure an int can't do anything exploititive
"""
async def clear_int(channel, param, integer):
    if integer <= 0:
        await channel.send(f"{param} must be creater than 0")
        return False

"""Allows the guild owner, administrators, bot moderators, and bot administrators to use mod commands"""
async def has_moderator(ctx):
    mod_id   = await GF.get_id(ctx.guild, "Mod")
    admin_id = await GF.get_id(ctx.guild, "Admin")

    if ctx.author.id == ctx.guild.owner.id: return True

    for role in ctx.author.roles:
        if role.id == mod_id or role.id == admin_id or role.permissions.administrator:
            return True

    return False

"""Gets sensitive keys"""
def get_value(key):
    with open(os.path.join(BASE_DIR, "hidden.json")) as f:
        return json.load(f)[key]

"""Searchs the database for ids needed in commands (Muted role, moderation role, channel id, etc)"""
async def get_id(guild, type):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT type_id FROM command_check WHERE server_id=? and type=?", (guild.id, type,))
    try:
        type_id = c.fetchone()[0]
        print(type_id)
        return type_id
    except:
        default = get(guild.roles, name="@everyone")
        perms = default.permissions
        perms.update(send_messages=False)
        role = await guild.create_role(name=type, permissions=perms)


        c.execute("INSERT INTO command_check (type_id, server_id, type) VALUES (?,?,?)", (role.id, guild.id, type,))
        conn.commit()
        conn.close()

        return role.id
