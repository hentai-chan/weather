#!/usr/bin/env python3

import argparse
import csv
import re
from collections import namedtuple
from typing import Optional

from pyowm.commons.exceptions import UnauthorizedError

from . import core, utils
from .__init__ import __version__, package_name
from .config import (BRIGHT, CONFIGFILE, GREEN, LOGFILE, MAGENTA, REPORTFILE,
                     RESET_ALL)
from .core import Mode, UnitSystem

#region argparse pseudo type checking

def validate_token(token: str) -> Optional[str]:
    if not re.match(r'[0-9a-f]{32}', token):
        err_msg = "It looks like you've entered an invalid API token. This incident will be reported."
        utils.logger.error(err_msg)
        utils.print_on_error(err_msg)
    else:
        return token

def validate_hour(hour: str) -> Optional[str]:
    if not hour.isnumeric() and int(hour) % 3 != 0:
        err_msg = "%s is not a valid number or evenly divisible by 3." % hour
        utils.logger.error(err_msg)
        utils.print_on_error(err_msg)
    else:
        return int(hour)

#endregion argparse pseudo type checking

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('--verbose', default=False, action='store_true', help="increase output verbosity")

    subparser = parser.add_subparsers(dest='command')

    log_parser = subparser.add_parser('log', help="read the log file")
    log_parser.add_argument('--path', action='store_true', help="return the log file path")
    log_parser.add_argument('--reset', action='store_true', help="purge the log file")
    log_parser.add_argument('--read', action='store_true', help='read the log file')

    config_parser = subparser.add_parser('config', help="configure default application settings")
    config_parser.add_argument('--token', nargs='?', type=validate_token, metavar="TOKEN", help="set OpenWeather API key")
    config_parser.add_argument('--location', nargs='?', type=str, help="set a default location")
    config_parser.add_argument('--unit-system', default=UnitSystem.SI, type=UnitSystem.from_string, choices=list(UnitSystem), help="set a default unit system")
    config_parser.add_argument('--path', action='store_true', help="return the log file path")
    config_parser.add_argument('--reset', action='store_true', help="purge the config file")
    config_parser.add_argument('--list', action='store_true', help="list all user configuration")

    report_parser = subparser.add_parser('report', help="generate a new weather report")
    report_parser.add_argument('--token', nargs='?', type=validate_token, metavar="TOKEN", help="set OpenWeather API key")
    report_parser.add_argument('--location', nargs='?', type=str, help="set a default location")
    report_parser.add_argument('--unit-system', default=UnitSystem.SI, type=UnitSystem.from_string, choices=list(UnitSystem), help="set a default unit system")
    report_parser.add_argument('--hour', default=15, nargs='?', type=validate_hour, metavar='HOUR', help="set hour for tomorrow's forecast (defaults to 15)")
    report_parser.add_argument('--mode', default=Mode.TODAY, type=Mode.from_string, choices=list(Mode), help="set new type of weather forecast (defaults to today)")
    report_parser.add_argument('--save', default=False, action='store_true', help="save weather report (default)")
    report_parser.add_argument('--no-save', dest='save', action='store_false', help="don't save weather report")
    report_parser.add_argument('--path', action='store_true', help="return the save file path")
    report_parser.add_argument('--reset', action='store_true', help="purge the save file")
    report_parser.add_argument('--read', action='store_true', help="read the save file")

    args = parser.parse_args()
    config_data = utils.read_json_file(CONFIGFILE)

    if args.command == 'log':
        logfile = utils.get_resource_path(LOGFILE)

        if args.path:
            return logfile
        if args.reset:
            utils.reset_file(logfile)
            return
        if args.read:
            with open(logfile, mode='r', encoding='utf-8') as file_handler:
                log = file_handler.readlines()

                if not log:
                    utils.print_on_warning("Nothing to read because the log file is empty")
                    return

                parse = lambda line: line.strip('\n').split('::')
                Entry = namedtuple('Entry', 'timestamp levelname lineno name message')

                tabulate = "{:<20} {:<5} {:<6} {:<14} {:<20}".format

                print('\n' + GREEN + tabulate('Timestamp', 'Line', 'Level', 'File Name', 'Message') + RESET_ALL)

                for line in log:
                    entry = Entry(parse(line)[0], parse(line)[1], parse(line)[2], parse(line)[3], parse(line)[4])
                    print(tabulate(entry.timestamp, entry.lineno.zfill(4), entry.levelname, entry.name, entry.message))

                print()

    if args.command == 'config':
        config_file = utils.get_resource_path(CONFIGFILE)

        if args.token:
            config_data['Token'] = args.token
            utils.write_json_file(CONFIGFILE, config_data)
        if args.location:
            config_data['Location'] = args.location
            utils.write_json_file(CONFIGFILE, config_data)
        if args.unit_system:
            config_data['UnitSystem'] = args.unit_system.name
            utils.write_json_file(CONFIGFILE, config_data)
        if args.path:
            return config_file
        if args.reset:
            utils.reset_file(config_file)
            return
        if args.list and config_data:
            utils.print_dict('Name', 'Value', config_data)
            return

    if args.command == 'report':
        report_file = utils.get_resource_path(REPORTFILE)

        if args.path:
            return report_file
        if args.reset:
            utils.reset_file(report_file)
            return
        if args.read:
            print()
            with open(report_file, mode='r', encoding='utf-8') as file_handler:
                reader = csv.DictReader(file_handler)
                tabulate = "{:<19}{:<10}{:<12}{:<16}{:<16}{:<16}{:<11}{:<10}{:<12}".format
                print(BRIGHT + GREEN + tabulate(*reader.fieldnames) + RESET_ALL)
                for row in list(reader):
                    print(tabulate(*row.values()))
            print()
            return

        try:
            weather_report = core.WeatherReport(
                args.token or config_data['Token'],
                args.location or config_data['Location'],
                args.unit_system.name or config_data['UnitSystem'],
                args.mode,
                args.hour
            )

            data = weather_report.build()

            if args.verbose:
                print(f"\n{BRIGHT}{MAGENTA}[ {RESET_ALL}Weather Report for {args.mode.value.capitalize()}{BRIGHT}{MAGENTA} ]{RESET_ALL}", sep='')
                data['Date'] = data['Date'].strftime('%B %d, %Y (%I:%M %p)')
                utils.print_dict('Name', 'Value', data)

            if not args.verbose:
                print(f"{BRIGHT}{MAGENTA}[ {RESET_ALL}{data['Date'].strftime('%B %d @ %I:%M %p')}{BRIGHT}{MAGENTA} ]{RESET_ALL} {data['TemperatureNow']} in {data['Location']}")

            if args.save:
                utils.write_csv(report_file, dict(zip(data.keys(), weather_report.export())))
                return

        except KeyError as key_error:
            utils.print_on_error("Encountered an error while trying to access %s in the configuration file." % str(key_error))
            utils.logger.error(str(key_error))
        except UnauthorizedError as auth_error:
            utils.print_on_error("Unauthorized access: OpenWeather denied servicing your request.")
            utils.logger.error(str(auth_error))
        except Exception as error:
            utils.print_on_error("Something unexpected happend. The responsible authorities have already been notified.")
            utils.logger.error(str(error))
