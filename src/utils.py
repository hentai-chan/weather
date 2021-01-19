#!/usr/bin/env python3

import json
from importlib.resources import path as resource_path

def read_configuration(resource: str, package: str) -> dict:
     with resource_path(resource, package) as resource_handler:
         with open(resource_handler, mode='r', encoding='utf-8') as file_handler:
             return json.load(file_handler)

def write_configuration(resource: str, package: str, params: dict) -> None:
     config = read_configuration(resource, package)
     with resource_path(resource, package) as resource_handler:
        with open(resource_handler, mode='w', encoding='utf-8') as file_handler:
            json.dump({**config, **params}, file_handler)