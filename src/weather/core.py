#!/usr/bin/env python3

from __future__ import annotations

import errno
import sys
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timedelta, timezone
from enum import Enum, unique
from typing import List, Optional, Tuple

import pyowm
from pyowm.weatherapi25.observation import Observation
from pyowm.weatherapi25.weather import Weather
from pyowm.weatherapi25.weather_manager import WeatherManager

from .config import BRIGHT, CYAN, DIM, GREEN, NORMAL, RED, RESET_ALL, YELLOW

#region argparse helpers

def from_template(cls, flag: str, selection: str) -> Optional[str]:
        try:
            return cls[selection.upper()]
        except KeyError:
            utils.print_on_error("Invalid option. Use: --%s {%s}" % (flag, ','.join([option.name.lower() for option in cls])))
            sys.exit(errno.EINVAL)

@unique
class Mode(Enum):
    TODAY = 'today'
    TOMORROW = 'tomorrow'

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_string(selection: str) -> Optional[str]:
        return from_template(Mode, 'mode', selection)


@unique
class UnitSystem(Enum):
    IMPERIAL = 'imperial'
    SI = 'si'

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_string(selection: str) -> Optional[str]:
        return from_template(UnitSystem, 'unit-system', selection)

#endregion argparse helpers

#region weather interface

UNITSYSTEM = [us.name for us in UnitSystem]

class WeatherReport(object):
    """
    Defines an interposed interface for the new PyOWM API.
    """
    _temperature_units: dict={'IMPERIAL': 'fahrenheit', 'SI': 'celsius'}
    _speed_units: dict={'IMPERIAL': 'miles_hour', 'SI': 'meters_sec'}
    _color_map = {
        range(-99, 0): DIM + CYAN,
        range(0, 5): NORMAL + CYAN,
        range(5, 10): BRIGHT + CYAN,
        range(10, 15): DIM + YELLOW,
        range(15, 20): NORMAL + YELLOW,
        range(20, 25): BRIGHT + YELLOW,
        range(25, 30): DIM + RED,
        range(30, 35): NORMAL + RED,
        range(35, 99): BRIGHT + RED
    }

    def __init__(self, token: str, location: str, unit_system: str, mode: Mode=Mode.TODAY, hour: int=3) -> WeatherReport:
        self.token = token
        self.location = location.capitalize()
        self.unit_system = unit_system.upper()
        self.mode = mode

        if hour % 3 != 0:
            raise ValueError("%d must be evenly divisible by 3." % hour)

        self.hour = hour


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(LOCATION={self.location})"

    @property
    def observation(self) -> Observation:
        weather_manager = pyowm.OWM(self.token).weather_manager()
        if self.mode == Mode.TODAY:
            return weather_manager.weather_at_place(self.location)
        else:
            return weather_manager.forecast_at_place(self.location, '3h')

    @property
    def datetime(self) -> dt:
        today = dt.today().astimezone(tz=timezone.utc)
        return today if self.mode == Mode.TODAY else today + timedelta(hours=12)

    @property
    def weather(self) -> Weather:
        if self.mode == Mode.TODAY:
            return self.observation.weather
        else:
            for weather in self.observation.forecast.weathers:
                ref_time = dt.fromtimestamp(weather.ref_time, tz=timezone.utc)
                if (ref_time.day > self.datetime.day and ref_time.hour == self.hour):
                    return weather

    @property
    def temperature(self):
        return self.weather.temperature(WeatherReport._temperature_units[self.unit_system.upper()])

    @property
    def temperature_min(self) -> float:
        return self.temperature['temp_min']

    @property
    def temperature_now(self) -> float:
        return self.temperature['temp']

    @property
    def temperature_max(self) -> float:
        return self.temperature['temp_max']

    @property
    def speed(self) -> float:
        return self.weather.wind(WeatherReport._speed_units[self.unit_system.upper()])['speed']

    @property
    def humidity(self) -> int:
        return self.weather.humidity

    @property
    def cloud_coverage(self) -> int:
        return self.weather.clouds

    @staticmethod
    def get_temperature_string(temperature: float, unit_system: str,) -> str:
        """
        Format the temperature using the passed unit system.
        """
        ensure_celsius = lambda temperature: (temperature - 32) / 1.8 if unit_system.upper() == 'IMPERIAL' else temperature
        temperature_string = "{:5.2F}{}C".format(temperature, u'\N{DEGREE SIGN}') if unit_system == 'SI' else "{:6.2F}{}F".format(temperature, u'\N{DEGREE SIGN}')
        return [f"{color}{temperature_string}{RESET_ALL}" for key, color in WeatherReport._color_map.items() if int(ensure_celsius(temperature)) in key][0]

    @staticmethod
    def get_wind_string(speed: float, unit_system: str) -> str:
        """
        Format the wind speed using the passed unit system.
        """
        return "{:5.2F}m/s".format(speed) if unit_system == 'SI' else f"{speed}mph"

    def build(self) -> dict:
        """
        Return a dictionary with pre-formatted strings.
        """
        padded_percentage = "{:5}%".format
        return {
            'Date': self.datetime,
            'Location': self.location,
            'UnitSystem': self.unit_system,
            'TemperatureMin': WeatherReport.get_temperature_string(self.temperature_min, self.unit_system),
            'TemperatureNow': WeatherReport.get_temperature_string(self.temperature_now, self.unit_system),
            'TemperatureMax': WeatherReport.get_temperature_string(self.temperature_max, self.unit_system),
            'WindSpeed': WeatherReport.get_wind_string(self.speed, self.unit_system),
            'Humidity': padded_percentage(self.humidity),
            'CloudCoverage': padded_percentage(self.weather.clouds)
        }

    def export(self) -> List[str]:
        """
        Return a list of data points fit for processing by other applications.
        """
        return list(map(str, [
            self.datetime.timestamp(),
            self.location,
            self.unit_system,
            self.temperature_min,
            self.temperature_now,
            self.temperature_max,
            self.speed,
            self.humidity,
            self.cloud_coverage
        ]))

#endregion weather interface
