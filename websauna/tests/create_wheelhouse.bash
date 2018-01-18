#!/bin/bash
#
# Create wheelhouse cache to speed up test_scaffold runs.
# Builds a wheelhouse folder containing al dependencies.
#
# $PYTHON_VERSION is like python3.5 or python3.6

set -e
# set -x

if [ -z "$PYTHON_VERSION" ] ; then
    PYTHON_VERSION=python3.5
fi

rm -rf /tmp/wheelhouse-venv
rm -rf wheelhouse/$PYTHON_VERSION
# $VIRTUALENV -q --no-site-packages -p $PYTHON_VERSION /tmp/wheelhouse-venv

$PYTHON_VERSION -m venv /tmp/wheelhouse-venv

source /tmp/wheelhouse-venv/bin/activate

# We cannot enable set -u before virtualenv activate has been run
set -u

# default pip is too old for 3.4
pip install -q -U pip

# We do the messages three phases as otherwise Travis considers our build stalled after 10m and I hope this solves this
echo "Installing project core dependencies."
pip install -q ".[celery,utils,notebook]"
echo "Installing project test dependencies."
pip install -q ".[test]"
echo "Installing project dev dependencies."
pip install -q ".[dev]"
pip install -q wheel
pip freeze > /tmp/wheelhouse-venv/requirements.txt

# websauna 0.0 development git branch should not go into freeze
echo "$(grep -v "websauna" /tmp/wheelhouse-venv/requirements.txt)" >/tmp/wheelhouse-venv/requirements.txt

# Build wheelhouse
echo "Building wheelhouse"
pip wheel -q -r /tmp/wheelhouse-venv/requirements.txt --wheel-dir wheelhouse/$PYTHON_VERSION