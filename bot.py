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
    name = ctx.author.name
    user_id = ctx.author.id
    prev_message = await ctx.send(
        'Gathering <@' + str(user_id) + '>\'s weather data...')

    if ctx.author.name not in user_cities:
        user_cities[name] = []
        message = no_city_message(user_id)
    else:
        message = f"<@{user_id}> Here is your weather report! :bar_chart:\n"
        temperatures = []
        for city, country in user_cities[name]:
            temp, warnings = get_temperature(name, city, country)
            temperatures.append(f'{city}, {country}: {temp}')
            message += f"**{city}**"
            if country != "":
                message += f", {country}"
            message += f" {temp}C°\n"
            if warnings != []:
                message += ':warning: Warnings:\n'
                for warning in warnings:
                    message += warning + "\n"
            message += "\n"
            # Record to file
    await prev_message.edit(content=f"{message}")


@bot.command(name="save")
async def save(ctx, city_name, country_code=""):
    a_file = open("cities.json", "w")
    city_name = city_name.upper()
    country_code = country_code.upper()
    if ctx.author.name not in user_cities:
        user_cities[ctx.author.name] = []
    if not ([city_name, country_code]) in user_cities[ctx.author.name]:
        user_cities[ctx.author.name].append([city_name, country_code])
        message = f"<@{ctx.author.id}> You have saved {city_name}."
    else:
        message = f"<@{ctx.author.id}> That city is already saved!"
    await ctx.send(message)
    json.dump(user_cities, a_file)
    a_file.close()


@bot.command(name="delete")
async def delete_city(ctx, city_name, country_code=""):
    city_name = city_name.upper()
    country_code = country_code.upper()
    name = ctx.author.name
    user_id = ctx.author.id
    a_file = open("cities.json", "w")

    if not user_has_cities(name):
        user_cities[name] = [(city_name, country_code)]
        await ctx.send(no_city_message(user_id))
    elif not [city_name, country_code] in user_cities[name]:
        await ctx.send(f"<@{user_id}> You don't have that city saved!")
    else:
        user_cities[name].remove([city_name, country_code])
        message = f"<@{user_id}> {city_name} deleted!"
        if user_has_cities(name):
            message += "\nYour remaining saved cities: "
            message += get_cities(name, user_id)
        await ctx.send(message)
    json.dump(user_cities, a_file)
    a_file.close()


@bot.command(name="cities")
async def cmd_get_cities(ctx):
    message = "<@" + str(ctx.author.id) + ">'s saved cities: "
    message += get_cities(ctx.author.name, ctx.author.id)
    await ctx.send(message)


def no_city_message(user_id):
    msg = "<@{}> you have no saved cities! " \
          "To do that, user the command !save [CITY] [COUNTRY CODE]."
    return msg.format(str(user_id))


def user_has_cities(user_name):
    if user_name not in user_cities or len(user_cities[user_name]) == 0:
        return False
    return True


def get_cities(user_name, user_id):
    if user_has_cities(user_name):
        cities = []
        for city, country in user_cities[user_name]:
            location = city
            if country != "":
                location += ", " + country
            cities.append(location)
        message = ""
        for city in cities:
            message += "\n" + city
    else:
        message = no_city_message(user_id)
    return message


def get_temperature(user_name, city, country):
    location = city
    if country != "":
        location += ", " + country

    input_arguments = {
        "location": location,
        "discordName": user_name
    }

    out = UiPathAuthentication.start_job(ACCESS_TOKEN, input_arguments)
    temp = str(out['main']['temp'])
    warnings = get_special_cond(temp, out['wind']['speed'],
                                out['main']['humidity'])
    return (temp, warnings)


def get_special_cond(temp, wind_speed, humidity):
    humid = float(humidity) >= 65
    dry = float(humidity) <= 30
    windy = float(wind_speed) >= 13.5
    hot = float(temp) >= 35
    cold = float(temp) <= 0
    warnings = []

    if humid:
        warnings.append(
            '-It appears to be a humid day, so make sure to stay hydrated and '
            'avoid outdoor activities! :droplet:')
    if dry:
        warnings.append(
            '-It appears to be a dry day, so make sure to stay hydrated and '
            'avoid outdoor activities and moisturize! :desert:')
    if hot:
        warnings.append(
            '-It appears to be a hot day, so make sure to stay hydrated, '
            'wear loose clothing, preferably of darker colors! :sun_with_face:')
    if windy:
        warnings.append(
            '-:exclamation: strong winds that may make it hard to walk, '
            'and make it colder in low temperatures. :wind_blowing_face:')
    if cold:
        warnings.append(
            '-:exclamation: low temperatures. wear warm clothes, '
            'and moisturize! :snowflake:')
    return warnings


bot.run(TOKEN)
