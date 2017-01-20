#!/bin/sh

echo "Downloading PianoL database"
# TODO: remove from dropbox
wget http://timba.nics.unicamp.br/mir_datasets/transcription/PianoL.zip --no-check-certificate
unzip PianoL.zip

echo "Downloading Piano database"
# TODO: remove from dropbox
wget http://timba.nics.unicamp.br/mir_datasets/transcription/Piano.zip --no-check-certificate
unzip Piano.zip
