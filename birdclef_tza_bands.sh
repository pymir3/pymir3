#!/usr/bin/env bash

python birdclef_tza_bands.py
rm dataset_features.csv
./pymir3-cl.py info features dataset_features.fm -cf > dataset_features.csv
./pymir3-cl.py info features dataset_features.fm -c >> dataset_features.csv
