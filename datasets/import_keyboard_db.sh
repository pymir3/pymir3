#!/bin/sh

echo "Downloading Keyboard database"
# TODO: remove from dropbox
wget http://www.dropbox.com/s/d40zfu74rw5s0rh/keyboard.zip --no-check-certificate
unzip keyboard.zip
