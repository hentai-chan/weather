#!/usr/bin/env python3

import json
from importlib.resources import path as resource_path
from itertools import chain

import click
from colorama import Fore, Style


def read_configuration() -> dict:
     with resource_path('src.data', 'config.json') as resource_handler:
         with open(resource_handler, mode='r', encoding='utf-8') as file_handler:
             return json.load(file_handler)

def write_configuration(params: dict) -> None:
     config = read_configuration()
     with resource_path('src.data', 'config.json') as resource_handler:
        with open(resource_handler, mode='w', encoding='utf-8') as file_handler:
            json.dump({**config, **params}, file_handler)

def reset_configuration() -> None:
    with resource_path('src.data', 'config.json') as resource_handler:
        with open(resource_handler, mode='w', encoding='utf-8') as file_handler:
            json.dump({}, file_handler)

def print_dict(title_left: str, title_right: str, table: dict) -> None:
    invert = lambda x: -x + (1 + len(max(chain(table.keys(), [title_left]), key=len)) // 8)
    tabs = lambda string: invert(len(string) // 8) * '\t'
    click.secho(f"\n{title_left}{tabs(title_left)}{title_right}", fg='green')
    click.echo(f"{len(title_left) * '-'}{tabs(title_left)}{len(title_right) * '-'}")
    for key, value in table.items():
            click.echo(f"{key}{tabs(key)}{value}")
    click.echo()

def print_on_success(message: str, verbose: bool=True) -> None:
    if verbose:
        click.secho(f"{Fore.GREEN}{'[  OK  ]'.ljust(10, ' ')}{Style.RESET_ALL}{message}")

def print_on_error(message: str, verbose: bool=True) -> None:
    if verbose:
        click.secho(f"{Fore.RED}{'[ ERROR ]'.ljust(10, ' ')}{Style.RESET_ALL}{message}", err=True)
