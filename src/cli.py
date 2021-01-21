#!/usr/bin/env python3

import re

import click
import pretty_errors
from colorama import Fore, Style

import src.core as core
import src.utils as utils
from src.__init__ import __version__, package_name
from src.core import UNITSYSTEM, Mode
from src.utils import color_string as c

CONTEXT_SETTINGS = dict(max_content_width=120)

class Token(click.ParamType):
    """
    Custom TokenParamType validator.
    """
    def convert(self, value, param, ctx):
        found = re.match(r'[0-9a-f]{32}', value)
        if not found:
            self.fail(c(f"{value} is not a 32-character hexadecimal string.", Fore.RED), param, ctx)
        return value

class Hour(click.ParamType):
    """
    Custom Hour validator.
    """
    def convert(self, value, param, ctx):
        hour = int(value)
        if hour % 3 != 0:
            self.fail(c(f"{value} is not evenly divisible by 3.", Fore.RED), param, ctx)
        return hour

@click.group(invoke_without_command=True, help=c("Simple script for reading weather data in the terminal.", Fore.GREEN), context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name=package_name, help=c("Show the version and exit.", Fore.YELLOW))
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['Configuration'] = utils.read_configuration()

@cli.command(help=c("Configure default application settings.", Fore.GREEN), context_settings=CONTEXT_SETTINGS)
@click.option('--token', type=Token(), help=c("Set OpenWeather API key.", Fore.YELLOW))
@click.option('--location', type=click.STRING, help=c("Set a default location.", Fore.YELLOW))
@click.option('--unit-system', type=click.Choice(UNITSYSTEM, case_sensitive=False), help=c("Set a default unit system.", Fore.YELLOW))
@click.option('--reset', is_flag=True, help=c("Reset all configurations.", Fore.YELLOW))
@click.option('--list', is_flag=True, help=c("List all app settings.", Fore.YELLOW))
@click.pass_context
def config(ctx, token, location, unit_system, reset, list):
    config = ctx.obj['Configuration']

    if token:
        config['Token'] = token
        utils.write_configuration(config)
    
    if location:
        config['Location'] = location
        utils.write_configuration(config)

    if unit_system:
        config['UnitSystem'] = unit_system.lower()
        utils.write_configuration(config)

    if reset:
        utils.reset_configuration()

    if list:
        click.secho("\nApplication Settings", fg='yellow')
        utils.print_dict('Name', 'Value', config)

@cli.command(help=c("Generate a new weather report.", Fore.GREEN), context_settings=CONTEXT_SETTINGS)
@click.option('--location', type=click.STRING, help=c("Configure weather report location.", Fore.YELLOW))
@click.option('--unit-system', type=click.Choice(UNITSYSTEM, case_sensitive=False), help=c("Set new unit system. Defaults to SI.", Fore.YELLOW))
@click.option('--mode', type=click.Choice([mode.value for mode in Mode], case_sensitive=False), default=Mode.Today.value, help=c("Set new type of weather forecast. Defaults to current (today).", Fore.YELLOW))
@click.option('--hour', type=Hour(), default=15, help=c("Set hour for tomorrow's forecast. Defaults to 15.", Fore.YELLOW))
@click.option('--verbose', is_flag=True, help=c("Enable verbose application output.", Fore.YELLOW))
@click.pass_context
def report(ctx, location, unit_system, mode, hour, verbose):
    config = ctx.obj['Configuration']
    token = config['Token']
    unit_system = unit_system or config.get('UnitSystem', 'SI')
    location = location or config.get('Location', 'New York, USA')
    core.formatted_weather_report(token, Mode(mode), location, unit_system, verbose, hour)
