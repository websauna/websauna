#!/bin/bash
#
# Create wheelhouse cache to speed up test_scaffold runs.
# Builds a wheelhouse folder containing al dependencies.
#

set -e
set -x
rm -rf /tmp/wheelhouse-venv
rm -rf wheelhouse
virtualenv-3.4 --no-site-packages /tmp/wheelhouse-venv
source /tmp/wheelhouse-venv/bin/activate
# default pip is too old for 3.4
# https://github.com/jnrbsn/daemonocle/issues/8
pip install --extra-index-url https://pypi.fury.io/uzQ6egqLUi1bcfHJehXv/miohtama/ -U pip
pip install --extra-index-url https://pypi.fury.io/uzQ6egqLUi1bcfHJehXv/miohtama/ .[test,dev]
pip install --extra-index-url https://pypi.fury.io/uzQ6egqLUi1bcfHJehXv/miohtama/ wheel
pip freeze > /tmp/wheelhouse-venv/requirements.txt
# websauna 0.0 development not available, remove from freeze
echo "$(grep -v "websauna" /tmp/wheelhouse-venv/requirements.txt)" >/tmp/wheelhouse-venv/requirements.txt
# sed -i '/websauna/d' /tmp/wheelhouse-venv/requirements.txt
# Needed for Daemonocle
pip wheel --extra-index-url https://pypi.fury.io/uzQ6egqLUi1bcfHJehXv/miohtama/ -r /tmp/wheelhouse-venv/requirements.txt