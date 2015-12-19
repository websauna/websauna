#!/bin/bash
#
# Create wheelhouse cache to speed up test_scaffold runs
#
#

set -e
rm -rf /tmp/wheelhouse-venv
rm -rf wheelhouse
virtualenv-3.4 --no-site-packages /tmp/wheelhouse-venv
source /tmp/wheelhouse-venv/bin/activate
pip install .
pip install wheel
pip freeze > /tmp/wheelhouse-venv/requirements.txt
# websauna 0.0 development not available, remove from freeze
echo "$(grep -v "websauna" /tmp/wheelhouse-venv/requirements.txt)" >/tmp/wheelhouse-venv/requirements.txt
# sed -i '/websauna/d' /tmp/wheelhouse-venv/requirements.txt
pip wheel -r /tmp/wheelhouse-venv/requirements.txt