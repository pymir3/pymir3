#!/usr/bin/env bash
echo "executando ballroom (one band)"
./experimento.py -d /home/juliano/birdclef/pymir3/mirex/file_lists -o fm -p ballroom.txt -e tzan

echo "executando bands"
./experimento.py -d /home/juliano/birdclef/pymir3/mirex/file_lists -o fm -p ballroom.txt -e bands

