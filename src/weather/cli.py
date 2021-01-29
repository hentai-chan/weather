#!/usr/bin/env python3

import re

import click
from click import style
from pyowm.commons.exceptions import UnauthorizedError

try:
    import pretty_errors
except ImportError:
    pass

from . import core, utils
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
@click.version_option(version=__version__, prog_name=package_name, help=style("Show the version and exit.", fg='yellow'))
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['CONFIGURATION'] = utils.read_resource('weather.data', 'config.json')

@cli.command(help=style("Perform log file operations.", fg='bright_green'), context_settings=CONTEXT_SETTINGS)
@click.option('--read', is_flag=True, default=False, help=style("Read the log file.", fg='yellow'))
@click.option('--reset', is_flag=True, default=False, help=style("Reset all log file entries", fg='yellow'))
@click.option('--path', is_flag=True, default=False, help=style("Get the log file path.", fg='yellow'))
def log(read, reset, path):
    if read:
        utils.read_log()
        return

    if reset:
        open(utils.log_file_path(target_dir=package_name), mode='w', encoding='utf-8').close()
        return

    if path:
        click.echo(utils.log_file_path(target_dir=package_name))
        return

@cli.command(help=style("Configure default application settings.", fg='bright_green'), context_settings=CONTEXT_SETTINGS)
@click.option('--token', type=Token(), help=style("Set OpenWeather API key.", fg='yellow'))
@click.option('--location', type=click.STRING, help=style("Set a default location.", fg='yellow'))
@click.option('--unit-system', type=click.Choice(UNITSYSTEM, case_sensitive=False), help=style("Set a default unit system.", fg='yellow'))
@click.option('--reset', is_flag=True, help=style("Reset all configurations.", fg='yellow'))
@click.option('--list', is_flag=True, help=style("List all app settings.", fg='yellow'))
@click.pass_context
def config(ctx, token, location, unit_system, reset, list):
    config = ctx.obj['CONFIGURATION']

    if token:
        config['Token'] = token
        utils.write_resource('weather.data', 'config.json', config)
    
    if location:
        config['Location'] = location
        utils.write_resource('weather.data', 'config.json', config)

    if unit_system:
        config['UnitSystem'] = unit_system.lower()
        utils.write_resource('weather.data', 'config.json', config)

    if reset:
        utils.reset_resource('weather.data', 'config.json')
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
@click.option('--save/--no-save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.option('--path', is_flag=True, default=False, help=style("Get the weather report path.", fg='yellow'))
@click.option('--verbose', is_flag=True, help=style("Enable verbose application output.", fg='yellow'))
@click.pass_context
def report(ctx, location, unit_system, mode, hour, save, path, verbose):
    config = ctx.obj['CONFIGURATION']

    if path:
        click.echo(utils.get_resource_path('weather.data', 'weather.json'))
        return
    
    try:
        token = config['Token']
        unit_system = unit_system or config.get('UnitSystem', 'SI')
        location = location or config.get('Location', 'Tokyo, Japan')
        core.formatted_weather_report(token, Mode(mode), location, unit_system, save, verbose, hour)
    except KeyError as exception:
        warning_message = f"Key Error: {exception}"
        utils.print_on_warning(warning_message)
        utils.logger.warning(warning_message)
    except UnauthorizedError as exception:
        error_message = f"{exception} (token={token})"
        utils.print_on_error(error_message)
        utils.logger.critical(error_message)
    except Exception as exception:
        utils.print_on_error("An unexpected error occurred. Please check the log file for more information.")
        utils.logger.critical(exception)
