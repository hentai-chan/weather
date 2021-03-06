#!/usr/bin/env python3

from datetime import datetime as dt
from datetime import timedelta, timezone
from enum import Enum, unique
from typing import Tuple

import click
import pyowm
from colorama import Fore, Style
from pyowm.weatherapi25.weather import Weather
from pyowm.weatherapi25.weather_manager import WeatherManager

from . import utils


@unique
class Mode(Enum):
    Today = 'today'
    Tomorrow = 'tomorrow'

UNITSYSTEM = ['IMPERIAL', 'SI']

_temperature_units = {'IMPERIAL': 'fahrenheit', 'SI': 'celsius'}
_speed_units = {'IMPERIAL': 'miles_hour', 'SI': 'meters_sec'}
_color_map = {
    range(-99, 0): f"{Style.DIM}{Fore.CYAN}",
    range(0, 5): f"{Style.NORMAL}{Fore.CYAN}",
    range(5, 10): f"{Style.BRIGHT}{Fore.CYAN}",
    range(10, 15): f"{Style.DIM}{Fore.YELLOW}",
    range(15, 20): f"{Style.NORMAL}{Fore.YELLOW}",
    range(20, 25): f"{Style.BRIGHT}{Fore.YELLOW}",
    range(20, 25): f"{Style.DIM}{Fore.RED}",
    range(25, 30): f"{Style.NORMAL}{Fore.RED}",
    range(30, 99): f"{Style.BRIGHT}{Fore.RED}",
}

def get_temperature_string(temperature: float, unit_system: str='SI') -> str:
    """
    Return a unit-decorated string representation of this temperature in color.
    """
    # convert temperature to celsius for reutilizing the color map definition
    ensure_celsius = lambda temperature: (temperature - 32) / 1.8 if unit_system.upper() == 'IMPERIAL' else temperature
    temperature_string = "{:5.2F}{}C".format(temperature, u'\N{DEGREE SIGN}') if unit_system.upper() == 'SI' else "{:6.2F}{}F".format(temperature, u'\N{DEGREE SIGN}')
    return [f"{color}{temperature_string}{Style.RESET_ALL}" for key, color in _color_map.items() if int(ensure_celsius(temperature)) in key][0]

def get_wind_string(speed: float, unit_system: str='SI') -> str:
    """
    Return the wind speed string representation matching the passed unit system.
    """
    return "{:5.2F}m/s".format(speed) if unit_system == 'SI' else f"{speed}mph"

def weather_manager(token: str) -> WeatherManager:
    """
    Initialize the OWM constructor and return a weather manager object.
    """
    return pyowm.OWM(token).weather_manager()

def raw_weather_report(weather: Weather, location: str, unit_system: str) -> dict:
    """
    Build a raw weather report feed dictionary. This method is useful for storing
    persistent data because the values contain no ANSI escape sequences or units.
    """
    temperature = weather.temperature(_temperature_units[unit_system.upper()])
    return {
        'DateTime': weather.ref_time,
        'Location': location,
        'Temperature (Min)': temperature['temp_min'],
        'Temperature (Now)': temperature['temp'],
        'Temperature (Max)': temperature['temp_max'],
        'Wind Speed': weather.wind(_speed_units[unit_system.upper()])['speed'],
        'Humidity': weather.humidity,
        'Cloud Coverage': weather.clouds
    }

def weather_report(weather: Weather, location: str, unit_system: str) -> dict:
    """
    Build a color-formatted weather report feed dictionary.
    """
    temperature = weather.temperature(_temperature_units[unit_system.upper()])
    padded_percentage = lambda value: "{:5}%".format(value)
    return {
        'Location': location,
        'Temperature (Min)': get_temperature_string(temperature['temp_min'], unit_system),
        'Temperature (Now)': get_temperature_string(temperature['temp'], unit_system),
        'Temperature (Max)': get_temperature_string(temperature['temp_max'], unit_system),
        'Wind Speed': get_wind_string(weather.wind(_speed_units[unit_system.upper()])['speed'], unit_system),
        'Humidity': padded_percentage(weather.humidity),
        'Cloud Coverage': padded_percentage(weather.clouds)
    }

def weather_today(token: str, location: str, unit_system: str='SI') -> Tuple[dict, dt]:
    """
    Return today's weather report and today's date as timezone-aware datetime object.
    """
    today = dt.today().astimezone(tz=timezone.utc)
    observation = weather_manager(token).weather_at_place(location)
    return weather_report(observation.weather, observation.location.name, unit_system), today

def weather_forecast(token: str, location: str, hour: int, unit_system: str='SI') -> Tuple[dict, dt]:
    """
    Return tomorrow's weather report targeted at `hour` o'clock and its reference
    time as timezone-aware datetime object. Note: `hour` must be evenly divisible by 3.
    """    
    forecaster = weather_manager(token).forecast_at_place(location, '3h')
    tomorrow = dt.today().astimezone(tz=timezone.utc) + timedelta(hours=12)

    if hour % 3 != 0:
        raise ValueError(f"{Fore.RED}{hour} must be evenly divisible by 3.{Style.RESET_ALL}")
    
    for weather in forecaster.forecast.weathers:
        ref_time = dt.fromtimestamp(weather.ref_time, tz=timezone.utc)
        if (ref_time.day > tomorrow.day and ref_time.hour == hour):
            return (weather_report(weather, forecaster.forecast.location.name, unit_system), ref_time)

def formatted_weather_report(token: str, mode: Mode, location: str, unit_system: str, save: bool, verbose: bool=False, hour: int=None) -> None:
    """
    Build a formatted weather report and print the result to the terminal.
    """
    with utils.CONSOLE.status('Reading weather report . . .', spinner='dots3') as _:
        report, dt_ = weather_today(token, location, unit_system) if mode is Mode.Today else weather_forecast(token, location, hour or 15, unit_system)

    if save:
        with utils.CONSOLE.status('Storing weather report . . .', spinner='dots3') as _:
            observation = weather_manager(token).weather_at_place(location)
            weather_history = utils.read_resource('weather.data', 'weather.json')
            tmp = weather_history.get(location, [])
            tmp.append(raw_weather_report(observation.weather, observation.location.name, 'SI'))
            weather_history[location] = tmp
            utils.write_resource('weather.data', 'weather.json', weather_history)
            utils.logger.info(f'Stored weather report for {location} today.')

    if verbose:
        click.secho(f"\n{Style.BRIGHT}{Fore.MAGENTA}[ {Style.RESET_ALL}{dt_.strftime('%B %d, %Y (%I:%M %p)')}{Fore.MAGENTA} ] {Style.RESET_ALL}", fg='magenta')
        utils.print_dict('Name', 'Value', report)
    else:
        click.echo(f"{Style.BRIGHT}{Fore.MAGENTA}[ {Style.RESET_ALL}{dt_.strftime('%B %d @ %I:%M %p')}{Fore.MAGENTA} ] {Style.RESET_ALL}", nl=False)
        click.echo(f"{report['Temperature (Now)']} ", nl = False)
        click.echo(f"in {report['Location']}")
