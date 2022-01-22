# WeathAvi Discord Bot
Built for the PyJac 2022 Competition, WeathAvi is a discord bot that can be added to servers to increase user's ease of access to weather data. The purpose of WeathAvi is twofold, to provide fundamental information to the public and critical information to pilots, particularly those in Canada and North America. Users have the ability to save (favourite) cities that they would like the weather for and can grab the weather along with alerts for most cities in the world. WeathAvi will provide appropriate recommendations for different climates, depending on if it is really arid, humid, hot, or cold. WeathAvi also provides important information from NAV Canada, with the ability to supply the METAR or TAF of different stations, grab station information, or even provide different analysis reports, depending on what the user needs.

## Durability
WeathAvi was made to be durable. It uses the [OpenWeatherMap](https://openweathermap.org/api) API for standard weather users and uses two different APIs for aviation-related commands. WeathAvi makes use of the [AVWX](https://avwx.rest/) and [CheckWX](https://www.checkwxapi.com/) APIs. This is to ensure that should one API not work, the other will kick in and step up to ensure users are still able to get the critical information they need. The root source for all charts and graphs is [NAV Canada](https://flightplanning.navcanada.ca/cgi-bin/CreePage.pl?Langue=anglais&NoSession=NS_Inconnu&Page=forecast-observation&TypeDoc=html).

## Peace of Mind
All commands are logged, meaning what the user requests from the bot and the bot output are all recorded and stored safely. This is to ensure there is proof if there happens to be an aircraft accident or incident investigation and WeathAvi happens to unfortunately take part.

## Usage & Commands
All WeathAvi bot commands start with an exclamation mark when you type a message. Below is a list of available commands that the user can utilize to communicate with WeathAvi.

***

### !weather
This command provides the user with the forecast for their saved cities. The forecast will includes any warnings to take note of and give suggestions to the user.

***

### !save `<city>` `<country_code>`
This command saves the specified city to the list of cities the user would like to look up the forecast for.

`city`: The city to add to the user's list.

`country_code`: The country where the city resides in in the format of a code.

***

### !delete `<city>` `<country_code>`
This command removes athe specified city from the list of cities the user would like to look up the forecast for.

`city`: The city to add to the user's list.

`country_code`: The country where the city resides in in the format of a code.

***

### !cities
This command lists the user's saved cities. Useful when the user wants to make changes to their saved favourites list.
***

### !metar `<station_name>`
This command provides the user with the most recent ***Meteorological Terminal Air Report (METAR)*** for the specified station using the **primary** API (CheckWX). Should the API fail, the seconcdary API will automatically be used. For help reading METARs, consider taking a glance at this [cheat sheet](https://www.weather.gov/media/wrh/mesowest/metar_decode_key.pdf). This command works for stations designated in ICAO or IATA around the globe.

`station_name`: The ICAO or IATA code.

***

### !metarB `<station_name>`
This command provides the user with the most recent ***Meteorological Terminal Air Report (METAR)*** for the specified station using the **secondary** API (AVWX). For help reading METARs, consider taking a glance at this [cheat sheet](https://www.weather.gov/media/wrh/mesowest/metar_decode_key.pdf). This command works for stations designated in ICAO or IATA around the globe.

`station_name`: The ICAO or IATA code.

***

### !taf `<station_name>`
This commands provides the user with the most recent ***Terminal Aerodrome Forecast (TAF)*** for the specified station using the **primary** API (CheckWX). Should the API fail, the secondary API will automatically be used. For help reading TAFs, consider taking a glance at this [cheat sheet](https://www.weather.gov/media/okx/Aviation/TAF_Card.pdf). This command works for stations designated in ICAO or IATA around the globe.

`station_name`: The ICAO or IATA code.

***

### !tafB `<station_name>`
This commands provides the user with the most recent ***Terminal Aerodrome Forecast (TAF)*** for the specified station using the **secondary** API (AVWX). For help reading TAFs, consider taking a glance at this [cheat sheet](https://www.weather.gov/media/okx/Aviation/TAF_Card.pdf). This command works for stations designated in ICAO or IATA around the globe.

`station_name`: The ICAO or IATA code.

***

### !gfa `<region>` `<map_type>` `<map_number>`
This command provides the user with the specified ***Graphical Area Forecast (GFA)***. Users must select a valid region or alias (listed below), an appropriate map type or alias (listed below) and a valid time (listed below). This command works only for stations designed in ICAO or IATA ***in Canada***.

`region`: The region that the GFA will display. Possible selections are:
 - **GFACN31 Pacific Region** - `(pacific, 31, bc)`
 - **GFACN32 Prairie Region** - `(prairie, 32, ab, sk, mb)`
 - **GFACN33 Ontario-Quebec Region** - `(ontario, quebec, 33, on, qc)`
 - **GFACN33 Atlantic Region** - `(atlantic, 34, nl, ns, nb, pe)`
 - **GFACN33 Yukon and Northwest Territories Region** - `(yukon, nwt, 35, ty, nt)`
 - **GFACN33 Nunavut Region** - `(nunavut, 36, nu)`
 - **GFACN33 Arctic Region** - `(arctic, 37)`
 - **All Region** - `(all)`

`map_type`: The type of map to display. Possible selections are:
 - **CLDWX (Clouds & Weather)** - `(cloud, weather, cw, cldwx)`
 - **TURBC (Icing, Turbulence & Freezing Levels** - `(icing, turb, turbulence, freeze, turbc)`
 - **All Map Types** - `(all)`

`map_number`: The validity time of the map. Possible selections are:
 - **Valid at 00 UTC** - `(1)`
 - **Valid at 06 UTC** - `(2)`
 - **Valid at 12 UTC** - `(3)`
 - **All Times** - `(all)`

***

### !station `<station_name>` `<option1>` `<option2>` `<option3>`
This command provides the user with ***general information*** pertaining to the specified station. All information will be fetched however depending on what the user requires according to the given arguments, only parts of the information will be displayed. The only required arguement is the `<station_name>`. Only providing the station name will result in the basic information being displayed. The user can provide additional arguements such as specifically receiving only the basic information using the argument `short` or getting the METAR and/or TAF with the respective arguments `METAR` and `TAF`. Options are interchangeable meaning the user can specity METAR in any of the 3 options slots. For exmaple, the following commands provide the same information: `!station taf metar long`, `!station long taf metar`. This command works for stations designated in ICAO or IATA around the globe.

`<station_name>`: The ICAO or IATA code.

`<option1>`:
 - **Include Only Basic Information** (by default) - `(short)`
 - **Include Additional Information** - `(long)`

`<option2>`:
 - **Include recent station METAR** - `(metar)`

`<option3>`:
 - **Include recent station TAF** - `(taf)`

***

### !full `<station_name>`
This command provides the user with a ***shortcut***. This command is equivalent to calling: `!station <station_name> long metar taf`. This command works for stations designated in ICAO or IATA around the globe.

`<station_name>`: The ICAO or IATA code.

***

### !partial `<station_name>`
This command provides the user with a ***shortcut***. This command is equivalent to calling: `!station <station_name> short metar taf`. This command works for stations designated in ICAO or IATA around the globe.

`<station_name>`: The ICAO or IATA code.

***

### !sigwx `<level>`
This command provides the user with the ***Significant Weather Prognastic Chart*** only for Canada. 

`<level>`: The level or region to display. Possible selections are:
 - **FL100 to FL240 (700 - 400 hPa)** - `(m, mid, middle)`
 - **FL250 to FL630** - `(h, hi, high)`
 - **Atlantic Region** - `(atlantic)`
 - **All Regions** - `(all)`

***

### !surface `<priority>`
This command provides the user with the ***Surface Analysis Chart*** only for Canada.

`<priority>`: The map release time relative to each other. Possible selections are:
 - **Latest Chart** - `(latest, l)`
 - **Previous Chart** - `(previous, prev, p)`
 - **All Priorities** - `(all)`

***

### !upperAir `<mb>` `<priority>`
This command provides the user with the ***Upper Air Analysis Chart*** only for Canada

`<mb>`: Height in millibars.
 - **250 mb (35 000')** - `(250)`
 - **500 mb (18 000')** - `(500)`
 - **700 mb (10 000')** - `(700)`
 - **All Heights** - `(all)`

`<priority>`: The map release time relative to each other. Possible selections are:
 - **Latest Chart** - `(latest, l)`
 - **Previous Chart** - `(previous, prev, p)`
 - **All Priorities** - `(all)`

***

### !turb `<location>`
This command provides the user with the specified ***Turbulence Forecast***.

`<location>`: The specified region to display. Possible selections are:
 - **Canadian Turbulence Forecast** - `(canada, ca, c)`
 - **North Atlantic Turbulence Forecast (Eastbound)** - `(eastbound, east, e)`
 - **North Atlantic Turbulence Forecast (Westbound)** - `(westbound, west, w)`
 - **All Locations** - `(all)`

