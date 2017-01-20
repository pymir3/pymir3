#!/bin/sh

echo "Downloading MIREX-based database"
# TODO: remove from dropbox
wget http://timba.nics.unicamp.br/mir_datasets/transcription/Mirex.zip --no-check-certificate
unzip Mirex.zip
