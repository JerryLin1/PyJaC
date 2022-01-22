import requests

# Main API (CheckWX) for METAR, TAF, Backup API for Station Info
X_API_KEY = 'bea8cbbadd5d4fe2a7a02225ec'

# Main API (AVWX) for Station Info, Backup API for METAR, TAF
API_KEY = 'iFuMmNyyB_zCHnCn_ueITKwl1eBPRg-0Nm-s4NhqfCs'


def get_metar(station):
    """
    Gets the METAR for the specified station using Main API.
    :param station: The station to get the METAR for.
    :return: The METAR for the specified station.
    """
    if station == '':
        return ':thermometer: **__METAR__**\nNo station specified, please ' \
               'specify a station in either ICAO or IATA format...\n\n'

    # Attempt main API
    response = requests.get('https://api.checkwx.com/metar/' + station.upper()
                            + '/decoded', headers={'X-API-Key': X_API_KEY})
    if response.json()['data']:
        report = response.json()['data'][0]['raw_text']

        return f':thermometer: **__METAR__**\n{report}\n\n'

    # Attempt backup API
    return get_backup_metar(station)


def get_backup_metar(station):
    """
    Gets the METAR for the specified station using Backup API.
    :param station: The station to get the METAR for.
    :return: The METAR for the specified station.
    """
    if station == '':
        return ':thermometer: **__METAR__**\nNo station specified, please ' \
               'specify a station in either ICAO or IATA format...\n\n'

    response = requests.get("https://avwx.rest/api/metar/" + station,
                            headers={"Authorization": "BEARER " + API_KEY})
    if response.status_code == 200:
        report = response.json()["raw"]
        return f':thermometer: **__METAR__ (BACKUP)**\n{report}\n\n'

    # METAR cannot be found for station
    report = 'METAR not available for this station. Check your spelling and ' \
             'make sure that the station is listed in ICAO or IATA...'
    return f':thermometer: **__METAR__**\n{report}\n\n'


def get_taf(station):
    """
    Gets the TAF for the specified station using Main API.
    :param station: The station to get the TAF for.
    :return: The TAF for the specified station.
    """
    if station == '':
        return ':thermometer: **__TAF__**\nNo station specified, please ' \
               'specify a station in either ICAO or IATA format...\n\n'

    response = requests.get('https://api.checkwx.com/taf/' + station.upper() +
                            '/decoded', headers={'X-API-Key': X_API_KEY})
    if response.json()['data']:
        report = response.json()['data'][0]['raw_text']
        return f':thermometer: **__TAF__**\n{report}\n\n'

    # Attempt backup API
    return get_backup_taf(station)


def get_backup_taf(station):
    """
    Gets the TAF for the specified station using Backup API.
    :param station: The station to get the TAF for.
    :return: The TAF for the specified station.
    """
    response = requests.get('https://avwx.rest/api/taf/' + station,
                            headers={"Authorization": "BEARER " + API_KEY})
    if response.status_code == 200:
        report = response.json()["raw"]
        return f':thermometer: **__TAF__ (BACKUP)**\n{report}\n\n'

    # TAF cannot be found for station
    report = 'TAF not available for this station. Check your spelling and ' \
             'make sure that the station is listed in ICAO or IATA...'
    return f':thermometer: **__TAF__**\n{report}\n\n'


def get_station(station):
    """
    Gets the station information for the given station using the Main API.
    :param station: The station to get information for.
    :return: The station information if available, otherwise None.
    """
    response = requests.get("https://avwx.rest/api/station/" + station,
                            headers={"Authorization": "BEARER " + API_KEY})
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def get_basic_info(response):
    """
    Grabs and formats some given station information from the Main API.
    :param response: The raw data.
    :return: Formatted station information.
    """
    name = response['name']
    icao = response['icao']
    iata = response['iata']
    location = response['city'] + ', ' + response['state'] + ', ' + \
        response['country']
    elevation = str(response['elevation_m']) + ' m' + ' (' + \
        str(response['elevation_ft']) + ' ft)'

    return f':flag_{response["country"].lower()}: ' \
           f'**__{icao} INFORMATION__**\n' \
           f'**Station Name:** {name}\n' \
           f'**Location**: {location}\n' \
           f'**ICAO**: {icao}\n' \
           f'**IATA**: {iata}\n' \
           f'**Elevation**: {elevation}\n\n'


def get_advanced_info(response):
    """
    Grabs and formats all given station information from the Main API.
    :param response: The raw data.
    :return: Formatted station information.
    """
    basic = get_basic_info(response)
    num_runways = len(response['runways'])
    runway_info = f':dividers: **__RUNWAY INFORMATION__**\n'

    for i in range(num_runways):
        runway_info += f'*Runway Ident 1:* ' \
                       f'{response["runways"][i]["ident1"]}\n' \
                       f'*Runway Ident 2:* ' \
                       f'{response["runways"][i]["ident2"]}\n' \
                       f'*Runway Length*: ' \
                       f'{response["runways"][i]["length_ft"]} ft\n' \
                       f'*Runway Width*: ' \
                       f'{response["runways"][i]["width_ft"]} ft\n\n'

    return basic + runway_info


def get_backup_station(station):
    """
    Gets the station information for the given station using the Backup API.
    :param station: The station to get information for.
    :return: The station information if available, otherwise None.
    """
    response = requests.get('https://api.checkwx.com/station/' +
                            station.upper(), headers={'X-API-Key': X_API_KEY})
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def get_backup_basic_info(response):
    """
    Grabs and formats some given station information from the Backup API.
    :param response: The raw data.
    :return: Formatted station information
    """
    name = response['data'][0]['name']
    icao = response['data'][0]['icao']
    iata = response['data'][0]['iata']
    location = response['data'][0]['city'] + ', ' + \
        response['data'][0]['state']['name'] + ', ' + \
        response['data'][0]['country']['name']
    elevation = str(response['data'][0]['elevation']['meters']) + 'm' + ' (' + \
        str(response['data'][0]['elevation']['feet']) + 'ft)'

    return f':flag_{response["country"].lower()}: ' \
           f'**__{icao} INFORMATION__ (BACKUP)**\n' \
           f'**Station Name:** {name}\n' \
           f'**Location**: {location}\n' \
           f'**ICAO**: {icao}\n' \
           f'**IATA**: {iata}\n' \
           f'**Elevation**: {elevation}\n\n'
