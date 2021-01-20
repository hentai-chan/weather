# Weather Terminal Application

In development.

## Setup

```bash
# access help page for this command
weather [command] --help
```

Get your API token from [OpenWeather](https://openweathermap.org/) and configure
your application:

```bash
weather config --token=<token>
```

Set your default unit system (either `si` or `imperial`):

```bash
weather config --unit-system=<system>
```

Set your default toponym:

```bash
#TODO: this is not implemented yet
weather config --location=<toponym>
```

Review your current configuration:

```bash
weather config --list
```

Discard all changes:

```bash
weather config --reset
```

## Basic Usage

Get today's weather data from Tokyo:

```bash
weather report tokyo
```

## Advanced Usage

Get tomorrow's weather forecast from tokyo displayed in imperial units:

```bash
#TODO: Implement verbose option
weather report tokyo --unit-system=imperial --mode=forecast_daily
```

Hint: run

```bash
weather report --help
```

to discover all available options.

## Installation

Serve this app locally by running

```bash
# create virtual environment & install dependencies
python -m venv venv/
source venv/bin/activate
pip install -e .
weather --version
```
