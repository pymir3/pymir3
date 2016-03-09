#!/usr/bin/env bash
echo "executando tzan (one band)"
./experimento.py -d ~/Dropbox/Doutorado/birdclef/pymir3/mirex/file_lists -o fm -p gtzan.txt -e tzan

echo "executando bands"
./experimento.py -d ~/Dropbox/Doutorado/birdclef/pymir3/mirex/file_lists -o fm -p gtzan.txt -e bands

