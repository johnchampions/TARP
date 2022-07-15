#! /bin/bash
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"
fullver=$(google-chrome --version)
set $fullver
IFS=.
read -ra ARR <<< $3
IFS= 
chromever=$(echo ${ARR[0]}.${ARR[1]}.${ARR[2]})
cd /tmp/
sudo wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$chromever
cdver=$(cat LATEST_RELEASE_$chromever)
sudo wget https://chromedriver.storage.googleapis.com/$cdver/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
chromedriver --version