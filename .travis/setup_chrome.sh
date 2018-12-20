#!/bin/bash
set -ev

# Install chromedriver - https://sites.google.com/a/chromium.org/chromedriver/
# This is not provided by Travis, but is needed by Selenium
wget -N http://chromedriver.storage.googleapis.com/2.36/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver
sudo mv chromedriver /usr/bin

# Make chrome available as "chrome"
sudo ln -s /usr/bin/google-chrome-stable /usr/bin/chrome
echo "Using chrome version $(chrome --version) from $(which chrome)"
echo "Using chromedriver version $(chromedriver --version) from $(which chromedriver)"
