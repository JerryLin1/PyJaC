import os
import json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

a_file = open("cities.json", "r")
user_cities = json.load(a_file)
a_file.close()


@bot.event
async def on_ready():
    print(type(user_cities))
    print('ready!')


@bot.command(name='weather')
async def send_weather(ctx):
    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = []
    message = user_cities[ctx.author.name]
    await ctx.send(message)


@bot.command(name="save")
async def save(ctx, city_name):
    a_file = open("cities.json", "w")

    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = [city_name]
    else:
        user_cities[ctx.author.name].append(city_name)
    json.dump(user_cities, a_file)
    a_file.close()
    await ctx.send("saved!")


    

bot.run(TOKEN)