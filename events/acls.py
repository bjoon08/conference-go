from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY

import json
import requests


def get_photo(city, state):
    url = "https://api.pexels.com/v1/search"
    params = {
        "per_page": 1,
        "query": city + " " + state,
    }
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, params=params, headers=headers)
    content = json.loads(response.content)

    try:
        return {
            "picture_url": content["photos"][0]["src"]["original"]
        }
    except (KeyError, IndexError):
        return {"picture_url": None}


def get_weather(city, state):
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    params_geo = {
        "appid": OPEN_WEATHER_API_KEY,
        "q": f"{city} {state}",
    }
    response = requests.get(geo_url, params=params_geo)
    content = json.loads(response.content)

    lat = content[0]["lat"]
    lon = content[0]["lon"]

    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params_weather = {
        "lat": lat,
        "lon": lon,
        "units": "imperial",
        "appid": OPEN_WEATHER_API_KEY,
    }
    response1 = requests.get(weather_url, params=params_weather)
    content1 = json.loads(response1.content)

    weather = {}
    weather["city"] = content1["name"]
    weather["temperature"] = content1["main"]["temp"]
    weather["description"] = content1["weather"][0]["description"]

    return weather
