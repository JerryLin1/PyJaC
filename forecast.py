import requests
import json
import os

api_key = os.getenv('API_KEY')


def get_forecast(city_name: str, country_id: str, units: str = 'metric') -> float:
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city_name},{country_id}&appid={api_key}&units={units}').text
    forecast = json.loads(response)
    return forecast
