import os
import json
from dotenv import load_dotenv
from discord.ext import commands
from forecast import get_forecast

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

a_file = open("cities.json", "r")
user_cities = json.load(a_file)
a_file.close()


@bot.event
async def on_ready():
    print('ready!')


@bot.command(name='weather')
async def send_weather(ctx):
    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = []
        message = 'You have no saved cities! To do that, user the command !save '
    else:
        temperatures = []
        for city, country in user_cities[ctx.author.name]:
            temp = str(get_forecast(city, country))
            temperatures.append(f'{city}, {country}: {temp}')
        message = temperatures
    await ctx.send(message)


@bot.command(name="save")
async def save(ctx, city_name, country_code):
    a_file = open("cities.json", "w")

    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = [(city_name, country_code)]
    else:
        user_cities[ctx.author.name].append((city_name.upper(), country_code.upper()))
    json.dump(user_cities, a_file)
    a_file.close()
    await ctx.send("saved!")


@bot.command(name="cities")
async def get_cities(ctx):
    cities = []
    for city, country in user_cities[ctx.author.name]:
        cities.append((f'{city}, {country}'))
    await ctx.send(cities)

bot.run(TOKEN)