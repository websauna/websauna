#!/bin/bash
#
# Setup test running for Ubuntu 12.02 / Drone IO
#
# As drone.io build command put:
#
#   # Launch the droneio test script from the repo
#   bash droneio.bash  # Wherever you put this script in your source code control
#
#

# Abort on error
set -e

# Set this flag if you want to debug output from the bash execution
set -x

# This is the name of the project and also name of the Python package
PROJECT_NAME=websauna

CHECKOUT_HOME=/home/ubuntu/src/bitbucket.org/miohtama/$PROJECT_NAME

# Need to upgrade to Python 3.5, at the writing of this drone.io only offers Python 3.3
sudo add-apt-repository ppa:fkrull/deadsnakes > /dev/null 2>&1
sudo apt-get -qq update > /dev/null 2>&1
sudo apt-get -qq install python3.5-dev > /dev/null 2>&1

# Creteat test virtualenv - we need to upgrade pip and virtualenv to good enough versions
sudo pip install -U pip virtualenv
virtualenv -p python3.5 venv
. venv/bin/activate

# Make sure pip itself is up to date
echo "Installing requirements"
# TODO: --extra-index-url -> a custom daemonocle release, waiting the upstream author for a release
pip install --extra-index-url https://pypi.fury.io/uzQ6egqLUi1bcfHJehXv/miohtama/ -e ".[test]" > /dev/null 2>&1

# Create PostgreSQL database for the tests
# http://docs.drone.io/databases.html - no IF NOT EXISTS for psql

export OLD_POSTGRESQL=1

set +e
psql -c 'CREATE DATABASE websauna_test;' -U postgres
set -e

# Make sure we have X11 set up so Selenium can launch Firefox
sudo start xvfb

# Code coverage setup
# https://pypi.python.org/pypi/coverage_enable_subprocess/0
pip install coverage-enable-subprocess
export COVERAGE_PROCESS_START=$PWD/.coveragerc

# Run tests using py.test test runner. We set timeout, so that if a test gets stuck it doesn't hang the run.
# We also print 10 slowest tests.
echo "Running tests"
py.test --splinter-webdriver=firefox --splinter-make-screenshot-on-failure=true --ini=droneio.ini --timeout=200 --durations=10 --cov-report xml --cov websauna --cov-config .coveragerc $PROJECT_NAME
echo "Done with tests"

# Upload coverage report to codecov
codecov --token=$CODECOV_TOK

# Show package versions to build output if all tests passed
pip freeze


