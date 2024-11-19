# e-footprint-interface

[![Django CI](https://github.com/publicissapient-france/e-footprint-interface/actions/workflows/ci.yml/badge.svg)](https://github.com/publicissapient-france/e-footprint-interface/actions/workflows/ci.yml)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Cypress.io](https://img.shields.io/badge/tested%20with-Cypress-04C38E.svg)](https://www.cypress.io/)

## Installation

### Windows

Prerequisite

[Python 3.10](https://www.python.org/downloads/release/python-3100/)

#### PyEnv

    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

#### Poetry

    py -m pip install --user pipx
    pipx install poetry

#### Dependencies installation

    poetry install
    npm install

## Run application

    poetry run python manage.py runserver


## Run tests

    poetry run python manage.py test
