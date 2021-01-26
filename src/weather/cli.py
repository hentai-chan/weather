#!/usr/bin/env python3

import re

import click
from click import style

try:
    import pretty_errors
except ImportError:
    pass

from . import core
from . import utils
from .__init__ import __version__, package_name
from .core import UNITSYSTEM, Mode

CONTEXT_SETTINGS = dict(max_content_width=120)

class Token(click.ParamType):
    """
    Custom TokenParamType validator.
    """
    name = 'token'
    def convert(self, value, param, ctx):
        found = re.match(r'[0-9a-f]{32}', value)
        if not found:
            error_message = f"{value} is not a 32-character hexadecimal string."
            utils.logger.error(error_message)
            self.fail(style(error_message, fg='red'), param, ctx)
        return value

class Hour(click.ParamType):
    """
    Custom Hour validator.
    """
    name = 'hour'
    def convert(self, value, param, ctx):
        hour = int(value)
        if hour % 3 != 0:
            error_message = f"{value} is not evenly divisible by 3."
            utils.logger.error(error_message)
            self.fail(style(error_message, fg='red'), param, ctx)
        return hour

@click.group(invoke_without_command=True, help=style("Simple script for reading weather data in the terminal.", fg='bright_magenta'), context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name=package_name, help="Show the version and exit.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['Configuration'] = utils.read_configuration()

@cli.command(help=style("Configure default application settings.", fg='bright_green'), context_settings=CONTEXT_SETTINGS)
@click.option('--token', type=Token(), help=style("Set OpenWeather API key.", fg='yellow'))
@click.option('--location', type=click.STRING, help=style("Set a default location.", fg='yellow'))
@click.option('--unit-system', type=click.Choice(UNITSYSTEM, case_sensitive=False), help=style("Set a default unit system.", fg='yellow'))
@click.option('--reset', is_flag=True, help=style("Reset all configurations.", fg='yellow'))
@click.option('--list', is_flag=True, help=style("List all app settings.", fg='yellow'))
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
        return

    if list:
        click.secho("\nApplication Settings", fg='bright_magenta')
        utils.print_dict('Name', 'Value', config)
        return

@cli.command(help=style("Generate a new weather report.", fg='bright_green'), context_settings=CONTEXT_SETTINGS)
@click.option('--location', type=click.STRING, help=style("Configure weather report location.", fg='yellow'))
@click.option('--unit-system', type=click.Choice(UNITSYSTEM, case_sensitive=False), help=style("Set new unit system. Defaults to SI.", fg='yellow'))
@click.option('--mode', type=click.Choice([mode.value for mode in Mode], case_sensitive=False), default=Mode.Today.value, help=style("Set new type of weather forecast. Defaults to today.", fg='yellow'))
@click.option('--hour', type=Hour(), default=15, help=style("Set hour for tomorrow's forecast. Defaults to 15.", fg='yellow'))
@click.option('--verbose', is_flag=True, help=style("Enable verbose application output.", fg='yellow'))
@click.pass_context
def report(ctx, location, unit_system, mode, hour, verbose):
    config = ctx.obj['Configuration']
    token = config['Token']
    unit_system = unit_system or config.get('UnitSystem', 'SI')
    location = location or config.get('Location', 'Tokyo, Japan')
    core.formatted_weather_report(token, Mode(mode), location, unit_system, verbose, hour)