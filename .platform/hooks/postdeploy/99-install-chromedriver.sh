#! /bin/bash
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"
fullver=$(google-chrome --version)
set $fullver
chromever=$(echo "${3%%.*}")
cd /tmp/
wget -q https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$chromever
cdver=$(cat LATEST_RELEASE_$chromever)
wget -q https://chromedriver.storage.googleapis.com/$cdver/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/chromedriver
chromedriver --version
