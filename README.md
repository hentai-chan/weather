<p align="center">
  <a title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/hentai-chan/weather/master/weather.svg">
  </a>
</p>

<h1 align="center">Weather Terminal Application</h1>

<p align="center">
    <a href="https://github.com/hentai-chan/weather" title="Release Version">
        <img src="https://img.shields.io/badge/Release-1.0.2%20-blue">
    </a>
    <a title="Supported Python Versions">
        <img src="https://img.shields.io/badge/Python-3.8%20-blue">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" title="License Information" target="_blank" rel="noopener noreferrer">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/hentai-chan/weather" title="Software Heritage Archive" target="_blank" rel="noopener noreferrer">
        <img src="https://archive.softwareheritage.org/badge/origin/https://github.com/hentai-chan/weather.git/">
    </a>
</p>

Weather is a modern terminal application for reading weather forecasts by harvesting
the OpenWeather API and features rich configuration options.

## Preview

Click on this image to watch a live demo on YouTube.

<p align="center">
  <a title="Project Logo" href="https://www.youtube.com/watch?v=JsCma_2iiMk">
    <img height="400" src="https://img.youtube.com/vi/JsCma_2iiMk/0.jpg">
  </a>
</p>

## Setup

Follow along the setup guide below to install and configure this terminal
application. Using an virtual environment is optional, but recommended. See also
`requirements.txt` to examine the dependency graph.

<details>
<summary>Installation</summary>

```cli
git clone https://github.com/hentai-chan/weather.git
cd weather/
python -m venv venv/
source venv/bin/activate
pip install -e .
# test installation
weather --version
```

</details>

## Configuration

Register a new account on <https://openweathermap.org/> to get your API token.

<details>
<summary>Customize Application Settings</summary>

**Mandatory:** Enter token:

```cli
weather config --token=<token>
```

**Optional:** Set your default unit system (either `si` or `imperial`):

```cli
weather config --unit-system=<system>
```

**Optional:** Set your default location as toponym (e.g. `Rome` or `New York, USA`):

```cli
weather config --location=<toponym>
```

**Optional:** Review your submissions:

```cli
weather config --list
```

**Optional:** Discard all settings:

```cli
weather config --reset
```

</details>

## Basic Usage

<details>
<summary>Command Line Usage</summary>

Get today's verbose weather forecast using default settings:

```cli
weather report --verbose
```

Get today's weather forecast for `New York, USA` in imperial units:

```cli
weather report --location="New York, USA" --unit-system=imperial
```

Get tomorrow's weather forecast for 12PM:

```cli
weather report --mode=tomorrow --hour=12
```

View the help page for this command:

```cli
weather report --help
```

</details>

## Report an Issue

Did something went wrong? Copy and paste the information from

```cli
weather --read-log
```

to file a new bug report.
