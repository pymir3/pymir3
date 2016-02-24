#!/bin/sh

echo "Downloading MIREX-based database"
# TODO: remove from dropbox
wget https://dl.dropboxusercontent.com/u/64294901/TrollData/mirex.zip --no-check-certificate
unzip mirex.zip
