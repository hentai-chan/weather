<p align="center">
  <a title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/hentai-chan/weather/master/weather.svg">
  </a>
</p>

<h1 align="center">Weather Terminal Application</h1>

Weather is a modern terminal application for reading weather forecasts by harvesting
the OpenWeather API and features rich configuration options.

## Preview

Click on this image to open a new window to see the live demo on YouTube.

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

```bash
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

```bash
weather config --token=<token>
```

**Optional:** Set your default unit system (either `si` or `imperial`):

```bash
weather config --unit-system=<system>
```

**Optional:** Set your default location as toponym (e.g. `Rome` or `New York, USA`):

```bash
weather config --location=<toponym>
```

**Optional:** Review your submissions:

```bash
weather config --list
```

**Optional:** Discard all settings:

```bash
weather config --reset
```

</details>

## Basic Usage

<details>
<summary>Customize Application Settings</summary>

Get today's verbose weather forecast using default settings:

```bash
weather report --verbose
```

Get today's weather forecast for `New York, USA` in imperial units:

```bash
weather report --location="New York, USA" --unit-system=imperial
```

Get tomorrow's weather forecast for 12PM:

```bash
weather report --mode=tomorrow --hour=12
```

View the help page for this command:

```bash
weather report --help
```

</details>
