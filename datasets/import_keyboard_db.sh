#!/bin/sh

echo "Downloading Keyboard database"
# TODO: remove from dropbox
wget http://timba.nics.unicamp.br/mir_datasets/transcription/keyboard.zip --no-check-certificate
unzip keyboard.zip
