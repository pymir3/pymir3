#!/bin/sh

echo "Downloading PianoL database"
# TODO: remove from dropbox
wget https://dl.dropboxusercontent.com/u/64294901/TrollData/PianoL.zip --no-check-certificate
unzip PianoL.zip

echo "Downloading Piano database"
# TODO: remove from dropbox
wget https://dl.dropboxusercontent.com/u/64294901/TrollData/Piano.zip --no-check-certificate
unzip Piano.zip
