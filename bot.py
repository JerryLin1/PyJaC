import os
import json
from dotenv import load_dotenv
from discord.ext import commands
import UiPathAuthentication


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

a_file = open("cities.json", "r")
user_cities = json.load(a_file)
a_file.close()
ACCESS_TOKEN = UiPathAuthentication.get_uipath_token()


@bot.event
async def on_ready():
    print('ready!')


@bot.command(name='weather')
async def send_weather(ctx):
    prev_message = await ctx.send('Gathering weather data...')

    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = []
        message = 'You have no saved cities! To do that, user the command !save'
    else:
        temperatures = []
        for city, country in user_cities[ctx.author.name]:
            temp, warnings = get_temperature(ctx.author.name, city, country)
            temperatures.append(f'{city}, {country}: {temp}')
            #Record to file
        message = temperatures
    await prev_message.edit(content=f"{message}")
    if warnings != []:
        await ctx.send('Warnings:')
    for warning in warnings:
        await ctx.send(warning)


@bot.command(name="save")
async def save(ctx, city_name, country_code):

    a_file = open("cities.json", "w")

    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = [(city_name, country_code)]
        message = "saved!"
    elif not ([city_name.upper(), country_code.upper()]) in user_cities[ctx.author.name]:
        user_cities[ctx.author.name].append((city_name.upper(), country_code.upper()))
        message = "saved!"
    else:
        messge = 'city already saved!'
    await ctx.send(message)
    json.dump(user_cities, a_file)
    a_file.close()

@bot.command(name="delete")
async def delete_city(ctx, city_name, country_code):
    a_file = open("cities.json", "w")

    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = [(city_name, country_code)]
        await ctx.send('You have no saved cities!')
    elif not [city_name.upper(), country_code.upper()] in user_cities[ctx.author.name]:
        await ctx.send('You do not have that city saved!')
    else:
        user_cities[ctx.author.name].remove([city_name, country_code])
        await ctx.send('City deleted!')
    json.dump(user_cities, a_file)
    a_file.close()

@bot.command(name="cities")
async def get_cities(ctx):
    cities = []
    if cities == []:
        await ctx.send('You have no saved cities!')
    else:
        for city, country in user_cities[ctx.author.name]:
            cities.append((f'{city}, {country}'))
        await ctx.send(cities)

def get_temperature(user_name, city, country):
    location = city + ',' + country

    input_arguments = {
                "location": location,
                "discordName": user_name
    }

    out = UiPathAuthentication.start_job(ACCESS_TOKEN, input_arguments)
    temp = str(out['main']['temp'])
    warnings = get_special_cond(temp, out['wind']['speed'], out['main']['humidity'])
    return (temp, warnings)

def get_special_cond(temp, wind_speed, humidity):
    humid = humidity >= 65
    dry = humidity <= 30
    windy = wind_speed >= 13.5
    hot = temp >= 35
    cold = temp <= 0
    warnings = []

    if humid:
        warnings.append('-It appears to be a humid day, so make sure to stay hydrated and avoid outdoor activities! :droplet:')
    if dry:
        warnings.append('-It appears to be a dry day, so make sure to stay hydrated and avoid outdoor activities and moisturize! :desert:')
    if hot:
        warnings.append('-It appears to be a hot day, so make sure to stay hydrated, wear loose clothing, preferably of darker colors! :sun_with_face:')
    if windy:
        warnings.append('-Warning :warning: strong winds that may make it hard to walk, and make it colder in low temperatures. :wind_blowing_face:')
    if cold:
        warnings.append('-Warning :warning: low temperatures. wear warm clothes, and moisturize! :snowflake:')
    return warnings
    



    
bot.run(TOKEN)