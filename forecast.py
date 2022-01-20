import requests
import json

api_key = "54eb010f04d6d698722f966769647d61"

def get_forecast(city_name: str, country_id: str, units: str = 'metric') -> float:
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city_name},{country_id}&appid={api_key}&units={units}').text
    forecast = json.loads(response)['main']['temp']
    return forecast
