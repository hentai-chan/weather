#!/usr/bin/env python3

from enum import Enum, unique

import pyowm
from pyowm.weatherapi25.one_call import OneCall

UNITSYSTEM = ['IMPERIAL', 'SI']

_temperature_units = {'IMPERIAL': 'fahrenheit', 'SI': 'celsius'}
_speed_units = {'IMPERIAL': 'miles_hour', 'SI': 'meters_sec'}
@unique
class Mode(Enum):
    Current = 'current'
    ForecastDaily = 'forecast_daily'
    ForecastHourly = 'forecast_hourly'
    ForecastMinutely = 'forecast_minutely'

def get_temperature_string(temperature: float, unit_system: str) -> str:
    return "{:05.2F}{}C".format(temperature, u'\N{DEGREE SIGN}') if unit_system == 'SI' else "{:06.2F}{}F".format(temperature, u'\N{DEGREE SIGN}')

def get_wind_string(speed: float, unit_system: str) -> str:
    return f"{speed}m/s" if unit_system == 'SI' else f"{speed}mph"

def query_owm_api(toponym: str, token: str) -> OneCall:
    owm = pyowm.OWM(token)
    registry = owm.city_id_registry()
    geo_points = registry.geopoints_for(toponym)[0]
    return owm.weather_manager().one_call(geo_points.lat, geo_points.lon)

def get_weather_data(toponym: str, unit_system: str, token: str, mode: Mode=Mode.Current) -> dict:
    weather = getattr(query_owm_api(toponym, token), mode.value)

    if mode is Mode.Current:
        return {
            'Location': ' '.join((str.capitalize() for str in toponym.split(' '))),
            'Temperature': get_temperature_string(weather.temperature(_temperature_units[unit_system.upper()])['temp'], unit_system),
            'Wind': get_wind_string(weather.wind(_speed_units[unit_system.upper()])['speed'], unit_system),
            'Humidity': f"{weather.humidity}%",
            'Cloud Coverage': f"{weather.clouds}%",
            'Atm. Pressure': f"{weather.pressure['press']}hpa"
        }
    elif mode is Mode.ForecastDaily:
        temperature = weather[0].temperature(_temperature_units[unit_system.upper()])
        return {
            'Temperature (Morn.)': get_temperature_string(temperature['morn'], unit_system),
            'Temperature (Day)': get_temperature_string(temperature['day'], unit_system),
            'Temperature (Eve.)': get_temperature_string(temperature['eve'], unit_system),
            'Temperature (Night)': get_temperature_string(temperature['night'], unit_system),
            'Temperature (Min.)': get_temperature_string(temperature['min'], unit_system),
            'Temperature (Max.)': get_temperature_string(temperature['max'], unit_system)
        }
    elif mode is Mode.ForecastHourly:
        return {
            'Temperature': get_temperature_string(weather[0].temperature(_temperature_units[unit_system.upper()])['temp'], unit_system)
        }
    else:
        raise NotImplementedError()
