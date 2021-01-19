# CLI Template

This is a template repository for CLI scripts written in python. We recommend
using `click` for parsing command line arguments, but any other library (like
`argparse`) could be used instead as well.

## Project Architecture

Using this template requires you to understand the project hierarchy, so here's
a quick rundown on the most important points:

1. `src` contains all code not directly related to packaging
2. `src/__init__.py` holds your version number, new releases should bump this value
   in accordance with [semantic versioning](https://semver.org/)
3. `src/__main__.py` is the entry point of your application, you shouldn't need
   to change anything here
4. `src/cli.py` defines your command line interface (CLI), but the business logic
   of your application should be placed in a separate file
5. `src/utils.py` contains general-purpose methods that could be used in any project
   of that nature, e.g. reading from and writing to configuration files, etc.
6. `src/core.py` defines your custom methods and serves as the backbone of your
   application

## User-Customization Checklist

Use the checklist below to customize this template for your project:

- [ ] Update all `[metadata]` in `setup.cfg` (see also <https://pypi.org/classifiers/>
      for a full list of classifiers)
- [ ] Configure your package name and version number in `src/__init__.py`
- [ ] Update `requirements.txt` (keep it in sync with `install_requires` in
      `setup.cfg` manually!)
- [ ] Check `.gitignore` and add/remove items from this list (e.g. name of your
      virtual environment)
- [ ] Update `.gitattributes` (the default configuration here should be fine as is)
- [ ] Choose a different license (uses GPLv3 by default)
- [ ] Update (or remove) `.markdownlint.json`
- [ ] Rewrite this readme file

If you want to use CI scripts for your project, now would be a good time to setup
your `yaml` files as well.

## Installation

Although this package is ready to go live on PyPI, you can still serve this locally
by running

```bash
# create virtual env and install dependencies
python -m venv venv/
source venv/bin/activate
pip install -e .
# test this script
cli-template --version
```
