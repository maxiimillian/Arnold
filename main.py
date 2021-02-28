import discord
import os
from .GlobalFunctions import GlobalFunctions as GF
import sqlite3
import os
from discord.ext import commands

#Absolute path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "cogs/db.db")

#Put your token in hidden.json
token = GF.get_value("token")

#Allows all intents, you may want to change this for your own uses
intents = discord.Intents().all()

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

#Files in cogs that should be ignored on initial loading
ignore_list = ["GlobalFunctions.py"]


#==============GETS SERVER SPECIFIC PREFIX==============
def get_prefix(bot, message):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT prefix FROM servers WHERE server_id=?", (message.guild.id,))
        result = c.fetchone()

        if result:
            return result[0]
        else:
            return '$'

#Loads the cogs
if __name__ == '__main__':
    for file in os.listdir("/home/pi/Arnold/cogs"):
        if file.endswith(".py") and file not in ignore_list:
            bot.load_extension(f'cogs.{file[:-3]}')
            print("Loaded: {}".format(file))


bot.run(,bot=True, reconnect=True)
