#!/usr/bin/env python3

import json
import logging
import os
import platform
import sys
from collections import namedtuple
from itertools import chain
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Union

from . import config
from .__init__ import package_name
from .config import BRIGHT, CYAN, DIM, GREEN, NORMAL, RED, RESET_ALL, YELLOW

#region logging

def get_config_dir() -> Path:
    """
    Return a platform-specific root directory for user configuration settings.
    """
    return {
        'Windows': Path(os.path.expandvars('%LOCALAPPDATA%')),
        'Darwin': Path.home().joinpath('Library').joinpath('Application Support'),
        'Linux': Path.home().joinpath('.config')
    }[platform.system()].joinpath(package_name)

def get_resource_path(filename: Union[str, Path]) -> Path:
    """
    Return a platform-specific log file path.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    resource = config_dir.joinpath(filename)
    resource.touch(exist_ok=True)
    return resource

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(lineno)d::%(name)s::%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler(get_resource_path(config.LOGFILE))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#endregion logging

#region misc

def read_json_file(filename: Union[str, Path]) -> dict:
    """
    TODO: test this method and write doc string
    """
    with open(get_resource_path(filename), mode='r', encoding='utf-8') as file_handler:
        try:
            return json.load(file_handler)
        except JSONDecodeError:
            return dict()

def write_json_file(filename: Union[str, Path], params: dict) -> None:
    """
    TODO: test this method and write doc string
    """
    config = read_json_file(filename)
    with open(get_resource_path(filename), mode='w', encoding='utf-8') as file_handler:
        json.dump({**config, **params}, file_handler)
        file_handler.write('\n')

def reset_file(filename: Union[str, Path]) -> None:
    open(get_resource_path(filename), mode='w', encoding='utf-8').close()


#endregion misc

#region terminal formatting

# TODO: break free from colorama dependency
def print_dict(title_left: str, title_right: str, table: dict) -> None:
    """
    Print a flat dictionary as table with two column titles.
    """
    print()
    table = {str(key): str(value) for key, value in table.items()}
    invert = lambda x: -x + (1 + len(max(chain(table.keys(), [title_left]), key=len)) // 8)
    tabs = lambda string: invert(len(string) // 8) * '\t'
    print(f"{GREEN}{title_left}{tabs(title_left)}{title_right}{RESET_ALL}")
    print(f"{len(title_left) * '-'}{tabs(title_left)}{len(title_right) * '-'}")
    for key, value in table.items():
        print(f"{key}{tabs(key)}{value}")
    print()

# TODO: break free from colorama dependency
def print_on_success(message: str, verbose: bool=True) -> None:
    """
    Print a formatted success message if verbose is enabled.
    """
    if verbose:
        print(f"{BRIGHT}{GREEN}{'[  OK  ]'.ljust(12, ' ')}{RESET_ALL}{message}")

# TODO: break free from colorama dependency
def print_on_warning(message: str, verbose: bool=True) -> None:
    """
    Print a formatted warning message if verbose is enabled.
    """
    if verbose:
        print(f"{BRIGHT}{YELLOW}{'[ WARNING ]'.ljust(12, ' ')}{RESET_ALL}{message}")

# TODO: break free from colorama dependency
def print_on_error(message: str, verbose: bool=True) -> None:
    """
    Print a formatted error message if verbose is enabled.
    """
    if verbose:
        print(f"{BRIGHT}{RED}{'[ ERROR ]'.ljust(12, ' ')}{RESET_ALL}{message}", file=sys.stderr)

def clear():
    """
    Reset terminal screen.
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')

#endregion
