import json

import requests
import  os
from dotenv import load_dotenv
from  urllib.request import urlopen


load_dotenv()
api_key  = os.getenv("API_TOKEN")

base_url = "http://api.openweathermap.org/data/2.5/weather?"

def kelvin_to_c(temp):
    return int(temp- 273.15)
def get_weather(city_name):
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    info = response.json()
    if info["cod"] != "404":
        main = info["main"]
        current_temperature = kelvin_to_c(main["temp"])
        current_pressure = main["pressure"]
        current_humidity = main["humidity"]
        description= info["weather"]
        weather_description = description[0]["description"]
        return current_temperature,current_pressure,current_humidity,weather_description
    else:
        return "404"

def get_current_location():
    url = "http://ipinfo.io/json"
    response = urlopen(url)
    data = json.load(response)
    return data['city']

