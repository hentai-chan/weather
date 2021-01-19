#!/usr/bin/env python3

import click
import pretty_errors

from src import utils
from src.core import square_function

from .__init__ import __version__, package_name


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name=package_name)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_configuration('src.data', 'config.json')

@cli.command(help="Prints hello world.")
@click.pass_context
def test(ctx):
    config = ctx.obj['CONFIG']

    # imported from config
    click.secho(config.get('Message', 'KeyNotFoundError'), fg='yellow')
    
    # imported from core
    click.echo("First ten powers of two:")
    for x, y in enumerate(square_function(1, 10)):
        click.echo(f"x={x+1}\ty={int(y)}")
