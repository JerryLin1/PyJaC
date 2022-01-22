import os
import json
from dotenv import load_dotenv
from discord.ext import commands
import UiPathAuthentication

import funcs
import quickstart

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
    print('WeathAvi is ready!')


# WEATHER SPECIFIC METHODS -----------------------------------------------------
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
            message += f"**{city}"
            if country != "":
                message += f", {country}"
            message += f" {temp}C°\n**"
            if warnings:  # equivalent to warning != []
                message += ':warning: Warnings:\n'
                for warning in warnings:
                    message += warning + "\n"
            message += "\n"
            # Record to file
    await prev_message.edit(content=f"{message}")


@bot.command(name="save")
async def save(ctx, city_name, country_code=""):
    file = open("cities.json", "w")
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
    json.dump(user_cities, file)
    file.close()


@bot.command(name="delete")
async def delete_city(ctx, city_name, country_code=""):
    city_name = city_name.upper()
    country_code = country_code.upper()
    name = ctx.author.name
    user_id = ctx.author.id
    file = open("cities.json", "w")

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
    json.dump(user_cities, file)
    file.close()


@bot.command(name="cities")
async def cmd_get_cities(ctx):
    message = "<@" + str(ctx.author.id) + ">'s saved cities: "
    message += get_cities(ctx.author.name, ctx.author.id)
    await ctx.send(message)


# WEATHER HELPER METHODS -------------------------------------------------------
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
    return temp, warnings


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


# AVIATION SPECIFIC METHODS ----------------------------------------------------
@bot.command(name='metar')
async def send_metar(ctx, station_name=''):
    temp = funcs.get_metar(station_name)
    quickstart.update_google_file(temp, ctx)
    await ctx.send(temp)


@bot.command(name='metarB')
async def send_backup_metar(ctx, station_name=''):
    temp = funcs.get_backup_metar(station_name)
    quickstart.update_google_file(temp, ctx)
    await ctx.send(temp)


@bot.command(name='taf')
async def send_taf(ctx, station_name=''):
    temp = funcs.get_taf(station_name)
    quickstart.update_google_file(temp, ctx)
    await ctx.send(temp)


@bot.command(name='tafB')
async def send_backup_taf(ctx, station_name=''):
    temp = funcs.get_backup_taf(station_name)
    quickstart.update_google_file(temp, ctx)
    await ctx.send(temp)


@bot.command(name='gfa')
async def send_gfa(ctx, region='', map_type='', map_number=''):
    await ctx.send(f':globe_with_meridians: **__GFA(s)__**\n')

    if region == '' and map_type == '' and map_number == '':
        await ctx.send(f'GFA(s) could not be found from the '
                       f'specified parameters...')
        return

    mapping = ''
    timing = ''
    about = ''

    mapping_all = ['cldwx', 'turbc']
    timing_all = ['000', '006', '012']
    about_all = ['gfacn31', 'gfacn32', 'gfacn33', 'gfacn34', 'gfacn35',
                 'gfacn36', 'gfacn37']

    mapping_dict = {'cldwx': 'Clouds & Weather',
                    'turbc': 'Icing, Turbulence & Freezing Levels'}
    timing_dict = {'000': '06 UTC', '006': '12 UTC', '012': '18 UTC'}
    about_dict = {'gfacn31': 'Pacific', 'gfacn32': 'Prairie',
                  'gfacn33': 'Ontario-Quebec', 'gfacn34': 'Atlantic',
                  'gfacn35': 'Yukon and NTW', 'gfacn36': 'Nunavut',
                  'gfacn37': 'Arctic'}

    mapping_bool = True
    timing_bool = True
    about_bool = True

    # Region
    if region.lower() in ['pacific', '31', 'bc']:
        about = 'gfacn31'
    elif region.lower() in ['prairie', '32', 'ab', 'sk', 'mb']:
        about = 'gfacn32'
    elif region.lower() in ['ontario', 'quebec', '33', 'on', 'qc']:
        about = 'gfacn33'
    elif region.lower() in ['atlantic', '34', 'nl', 'ns', 'nb', 'pe']:
        about = 'gfacn34'
    elif region.lower() in ['yukon', 'nwt', '35', 'yt', 'nt']:
        about = 'gfacn35'
    elif region.lower() in ['nunavut', '36', 'nu']:
        about = 'gfacn36'
    elif region.lower() in ['arctic', '37']:
        about = 'gfacn37'
    elif region.lower() == 'all':
        about = 'all'
    else:
        about_bool = False

    # Map type
    if map_type.lower() in ['cloud', 'weather', 'cw', 'cldwx']:
        mapping = 'cldwx'
    elif map_type.lower() in ['icing', 'turb', 'turbulence', 'freeze', 'turbc']:
        mapping = 'turbc'
    elif map_type.lower() == 'all':
        mapping = 'all'
    else:
        mapping_bool = False

    # Time
    if map_number == '1':
        timing = '000'
    elif map_number == '2':
        timing = '006'
    elif map_number == '3':
        timing = '012'
    elif map_number == 'all':
        timing = 'all'
    else:
        timing_bool = False

    # Send the map
    if mapping_bool and timing_bool and about_bool:
        if about == 'all' and mapping == 'all' and timing == 'all':
            for i in about_all:
                for j in mapping_all:
                    for k in timing_all:
                        await ctx.send(
                            f'**REGION:** {about_dict.get(i)}\n'
                            f'**MAP TYPE:** {mapping_dict.get(j)}\n'
                            f'**VALID UNTIL:** {timing_dict.get(k)}')
                        await ctx.send(
                            f'https://flightplanning.navcanada.ca/Latest'
                            f'/gfa/anglais/produits/uprair/gfa/{i}/'
                            f'Latest-{i}_{j}_{k}.png\n')
        elif about == 'all' and mapping == 'all':
            for i in about_all:
                for j in mapping_all:
                    await ctx.send(
                        f'**REGION:** {about_dict.get(i)}\n'
                        f'**MAP TYPE:** {mapping_dict.get(j)}\n'
                        f'**VALID UNTIL:** {timing_dict.get(timing)}')
                    await ctx.send(
                        f'https://flightplanning.navcanada.ca/'
                        f'Latest/gfa/anglais/produits/uprair/gfa/{i}/'
                        f'Latest-{i}_{j}_{timing}.png')
        elif about == 'all' and timing == 'all':
            for i in about_all:
                for k in timing_all:
                    await ctx.send(
                        f'**REGION:** {about_dict.get(i)}\n'
                        f'**MAP TYPE:** {mapping_dict.get(mapping)}\n'
                        f'**VALID UNTIL:** {timing_dict.get(k)}')
                    await ctx.send(
                        f'https://flightplanning.navcanada.ca/Latest/'
                        f'gfa/anglais/produits/uprair/gfa/{i}/'
                        f'Latest-{i}_{mapping}_{k}.png')
        elif mapping == 'all' and timing == 'all':
            for j in mapping_all:
                for k in timing_all:
                    await ctx.send(
                        f'**REGION:** {about_dict.get(about)}\n'
                        f'**MAP TYPE:** {mapping_dict.get(j)}\n'
                        f'**VALID UNTIL:** {timing_dict.get(k)}')
                    await ctx.send(
                        f'https://flightplanning.navcanada.ca/Latest/'
                        f'gfa/anglais/produits/uprair/gfa/{about}/'
                        f'Latest-{about}_{j}_{k}.png')
        elif about == 'all':
            for i in about_all:
                await ctx.send(
                    f'**REGION:** {about_dict.get(i)}\n'
                    f'**MAP TYPE:** {mapping_dict.get(mapping)}\n'
                    f'**VALID UNTIL:** {timing_dict.get(timing)}')
                await ctx.send(
                    f'https://flightplanning.navcanada.ca/Latest'
                    f'/gfa/anglais/produits/uprair/gfa/{i}/'
                    f'Latest-{i}_{mapping}_{timing}.png')
        elif mapping == 'all':
            for j in mapping_all:
                await ctx.send(
                    f'**REGION:** {about_dict.get(about)}\n'
                    f'**MAP TYPE:** {mapping_dict.get(j)}\n'
                    f'**VALID UNTIL:** {timing_dict.get(timing)}')
                await ctx.send(
                    f'https://flightplanning.navcanada.ca/Latest/'
                    f'gfa/anglais/produits/uprair/gfa/{about}/'
                    f'Latest-{about}_{j}_{timing}.png')
        elif timing == 'all':
            for k in timing_all:
                await ctx.send(
                    f'**REGION:** {about_dict.get(about)}\n'
                    f'**MAP TYPE:** {mapping_dict.get(mapping)}\n'
                    f'**VALID UNTIL:** {timing_dict.get(k)}')
                await ctx.send(
                    f'https://flightplanning.navcanada.ca/Latest/'
                    f'gfa/anglais/produits/uprair/gfa/{about}/'
                    f'Latest-{about}_{mapping}_{k}.png')
        else:
            await ctx.send(
                f'**REGION:** {about_dict.get(about)}\n'
                f'**MAP TYPE:** {mapping_dict.get(mapping)}\n'
                f'**VALID UNTIL:** {timing_dict.get(timing)}')
            await ctx.send(
                f'https://flightplanning.navcanada.ca/Latest/'
                f'gfa/anglais/produits/uprair/gfa/{about}/'
                f'Latest-{about}_{mapping}_{timing}.png')
    else:
        await ctx.send(f'GFA(s) could not be found from the '
                       f'specified parameters...')


@bot.command(name='station')
async def send_station(ctx, station_name="", detail1="", detail2="",
                       detail3=""):
    if station_name == "":
        data = ':earth_americas: **__STATION INFORMATION__**\n' \
               'No station specified, please specify a station in ' \
               'either ICAO or IATA format...\n\n'

        quickstart.update_google_file(data, ctx)
        await ctx.send(data)
        return

    # Check for extra details
    long = detail1.lower() == 'long' or detail2.lower() == 'long' or \
        detail3.lower() == 'long'
    metar = detail1.lower() == 'metar' or detail2.lower() == 'metar' or \
        detail3.lower() == 'metar'
    taf = detail1.lower() == 'taf' or detail2.lower() == 'taf' or \
        detail3.lower() == 'taf'

    # Get data, if possible
    temp = funcs.get_station(station_name)
    if temp is None:  # No data from first source
        temp2 = funcs.get_backup_station(station_name)
        if not temp2['data']:  # No data from second source
            data = ':earth_americas: **__STATION INFORMATION__**\n' \
                   'Invalid station specified, please specify a station in ' \
                   'either ICAO or IATA format...\n\n'
            quickstart.update_google_file(data, ctx)
            await ctx.send(data)
        else:  # Data from second source
            ret = funcs.get_backup_basic_info(temp2)

            if metar:
                ret += funcs.get_metar(temp2['data'][0]['icao'])
            if taf:
                ret += funcs.get_taf(temp2['data'][0]['icao'])

            quickstart.update_google_file(ret, ctx)
            await ctx.send(ret)

    else:  # Data from first source
        ret = ''

        if long:
            ret += (funcs.get_advanced_info(temp))
        else:
            ret += (funcs.get_basic_info(temp))

        if metar:
            ret += (funcs.get_metar(temp["icao"]))
        if taf:
            ret += (funcs.get_taf(temp["icao"]))

        quickstart.update_google_file(ret, ctx)
        await ctx.send(ret)


@bot.command(name='full')
async def send_full_info(ctx, station_name):
    await send_station(ctx, station_name, 'long', 'metar', 'taf', )


@bot.command(name='partial')
async def send_partial_info(ctx, station_name):
    await send_station(ctx, station_name, 'short', 'metar', 'taf')


@bot.command(name='sigwx')
async def send_sigwx(ctx, level=''):
    if level == '':
        await ctx.send(':map: **__SIGWX INFORMATION__**\n'
                       'No level specified, please specify a level...\n\n')
        return

    title_dict = {'m': f':map: '
                       f'**__Significant Weather Prognostic Chart MID LVL__**',
                  'h': f':map: '
                       f'**__Significant Weather Prognostic Chart HIGH LVL__**',
                  'a': f':map: '
                       f'**__Significant Weather Prognostic Chart ATLANTIC__**'}

    mapping_dict = {'m': 'https://flightplanning.navcanada.ca/Latest/'
                         'anglais/produits/uprair/sigwx/FL100-FL240/'
                         'Latest-sigwx-fl100-fl240.png',
                    'h': 'https://flightplanning.navcanada.ca/Latest/'
                         'anglais/produits/uprair/sigwx/FL250-FL630/'
                         'Latest-sigwx_fl250-fl630.png',
                    'a': 'https://flightplanning.navcanada.ca/Latest/'
                         'anglais/produits/uprair/sigwx/atlantic/'
                         'Latest-sigwx-atlantic.png'}

    if level.lower() in ['m', 'mid', 'middle']:
        await ctx.send(title_dict.get('m'))
        await ctx.send(mapping_dict.get('m'))
    elif level.lower() in ['h', 'hi', 'high']:
        await ctx.send(title_dict.get('h'))
        await ctx.send(mapping_dict.get('h'))
    elif level.lower() == 'atlantic':
        await ctx.send(title_dict.get('a'))
        await ctx.send(mapping_dict.get('a'))
    elif level.lower() == 'all':
        await ctx.send(title_dict.get('m'))
        await ctx.send(mapping_dict.get('m'))
        await ctx.send(title_dict.get('h'))
        await ctx.send(mapping_dict.get('h'))
        await ctx.send(title_dict.get('a'))
        await ctx.send(mapping_dict.get('a'))
    else:
        await ctx.send(':map: **__SIGWX INFORMATION__**\n'
                       'Invalid level specified, please specify a level...\n\n')


@bot.command(name='surface')
async def send_surface_analysis(ctx, time=''):
    if time == '':
        await ctx.send(':map: **__SURFACE ANALYSIS__**\n'
                       'No time specified, please specify a time...\n\n')
        return

    title_dict = {'l': f':map: **__Surface Analysis__ (Latest)**',
                  'p': f':map: **__Surface Analysis__ (Previous)**'}

    mapping_dict = {'l': 'https://flightplanning.navcanada.ca/Latest/'
                         'anglais/produits/analyses/surface/'
                         'Latest-analsfc.png',
                    'p': 'https://flightplanning.navcanada.ca/Latest/'
                         'anglais/produits/analyses/surface/'
                         'LatestPrev-analsfc.png'}

    if time.lower() in ['latest', 'l']:
        await ctx.send(title_dict.get('l'))
        await ctx.send(mapping_dict.get('l'))
    elif time.lower() in ['prev', 'p', 'previous']:
        await ctx.send(title_dict.get('p'))
        await ctx.send(mapping_dict.get('p'))
    elif time.lower() == 'all':
        await ctx.send(title_dict.get('l'))
        await ctx.send(mapping_dict.get('l'))
        await ctx.send(title_dict.get('p'))
        await ctx.send(mapping_dict.get('p'))
    else:
        await ctx.send(':map: **__SURFACE ANALYSIS__**\n'
                       'Invalid time specified, please specify a time...\n\n')


@bot.command(name='upperAir')
async def send_upper_air_analysis(ctx, mb_given: str = '',
                                  time_given: str = ''):
    if mb_given == '' or time_given == '':
        await ctx.send(':map: **__UPPER AIR ANALYSIS__**\n'
                       'No mb or time specified, '
                       'please specify a mb and time...\n\n')
        return

    mb = ''
    time = ''

    mb_all = ['250', '500', '700']
    time_all = ['previous', 'latest']

    mb_dict = {'250': '64 000\'',
               '500': '18 000\'',
               '700': '10 000\''}

    time_dict = {'latest': ('Latest', 'Latest'),
                 'previous': ('Previous', 'LatestPrev')}

    mb_bool = True
    time_bool = True

    # Map type
    if mb_given in ['250', '500', '700']:
        mb = mb_given
    elif mb_given == 'all':
        mb = 'all'
    else:
        mb_bool = False

    # Map time
    if time_given.lower() in ['latest', 'l']:
        time = 'latest'
    elif time_given.lower() in ['prev', 'p', 'previous']:
        time = 'previous'
    elif time_given.lower() == 'all':
        time = 'all'
    else:
        time_bool = False

    # Send the map
    if mb_bool and time_bool:
        if mb == 'all' and time == 'all':
            for i in mb_all:
                for j in time_all:
                    await ctx.send(f':map: **__Upper Air Analysis__ ('
                                   f'{time_dict.get(j)[0]})**\n**Level**: '
                                   f'{i} mb ({mb_dict.get(i)})\n')
                    await ctx.send(f'https://flightplanning.navcanada.ca/'
                                   f'Latest/anglais/produits/analyses/'
                                   f'altitude/{time_dict.get(j)[1]}-anal{i}.'
                                   f'png')
        elif mb == 'all':
            for i in mb_all:
                await ctx.send(f':map: **__Upper Air Analysis__ ('
                               f'{time_dict.get(time)[0]})**\n**Level**: '
                               f'{i} mb ({mb_dict.get(i)})\n')
                await ctx.send(f'https://flightplanning.navcanada.ca/'
                               f'Latest/anglais/produits/analyses/'
                               f'altitude/{time_dict.get(time)[1]}-anal{i}.png')
        elif time == 'all':
            for j in time_all:
                await ctx.send(f':map: **__Upper Air Analysis__ ('
                               f'{time_dict.get(j)[0]})**\n**Level**: '
                               f'{mb} mb ({mb_dict.get(mb)})\n')
                await ctx.send(f'https://flightplanning.navcanada.ca/'
                               f'Latest/anglais/produits/analyses/'
                               f'altitude/{time_dict.get(j)[1]}-anal{mb}.png')
        else:
            await ctx.send(f':map: **__Upper Air Analysis__ ('
                           f'{time_dict.get(time)[0]})**\n**Level**: '
                           f'{mb} mb ({mb_dict.get(mb)})\n')
            await ctx.send(f'https://flightplanning.navcanada.ca/Latest/'
                           f'anglais/produits/analyses/altitude/'
                           f'{time_dict.get(time)[1]}-anal{mb}.png')
    else:
        await ctx.send(':map: **__UPPER AIR ANALYSIS__**\n'
                       'Invalid mb or time specified, '
                       'please specify a mb and time...\n\n')


@bot.command(name='turb')
async def send_turb_report(ctx, location: str = ''):
    if location == '':
        await ctx.send(':warning: **__TURBULENCE REPORT__**\n'
                       'No location specified, '
                       'please specify a location...\n\n')
        return

    title_dict = {'c': (':warning: '
                        '**__Canadian Turbulence Forecast__**', '-hltcan'),
                  'e': (':warning: '
                        '**__North Atlantic Turbulence Forecast__ '
                        '(Eastbound)**', '00-est'),
                  'w': (':warning: '
                        '**__North Atlantic Turbulence Forecast__ '
                        '(Westbound)**', '11-ouest')}

    if location.lower() in ['ca', 'canada', 'c']:
        direction = title_dict.get('c')
        await ctx.send(direction[0])
        await ctx.send(f'https://flightplanning.navcanada.ca/Latest/'
                       f'anglais/produits/uprair/turb-haut-niv/'
                       f'Latest{direction[1]}.png')

    elif location.lower() in ['e', 'east', 'eastbound']:
        direction = title_dict.get('e')
        await ctx.send(direction[0])
        await ctx.send(f'https://flightplanning.navcanada.ca/Latest/'
                       f'anglais/produits/uprair/turb-haut-niv/'
                       f'Latest{direction[1]}.png')

    elif location.lower() in ['w', 'west', 'westbound']:
        direction = title_dict.get('w')
        await ctx.send(direction[0])
        await ctx.send(f'https://flightplanning.navcanada.ca/Latest/'
                       f'anglais/produits/uprair/turb-haut-niv/'
                       f'Latest{direction[1]}.png')
    elif location.lower() == 'all':
        for i in title_dict.keys():
            direction = title_dict.get(i)
            await ctx.send(direction[0])
            await ctx.send(f'https://flightplanning.navcanada.ca/Latest/'
                           f'anglais/produits/uprair/turb-haut-niv/'
                           f'Latest{direction[1]}.png')
    else:
        await ctx.send(':warning: **__TURBULENCE REPORT__**\n'
                       'Invalid location specified, '
                       'please specify a location...\n\n')


bot.run(TOKEN)
