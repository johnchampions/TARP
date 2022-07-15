#! /bin/bash
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"
ver=$(google-chrome --version)
set $ver
cd /tmp/
sudo wget https://chromedriver.storage.googleapis.com/$3/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
chromedriver --version