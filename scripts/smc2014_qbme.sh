#!/bin/bash
set -o errexit


scripts/clean.sh datasets/Textures/Audio/
scripts/dataset_features.sh datasets/Textures/Audio/

echo "Musician M1"
scripts/recommendation_test.sh pcabayes daasets/Textures/Audio/ datasets/Textures/Label/adriano_in.txt datasets/Textures/Label/adriano_out.txt

echo "Musician M2"
scripts/recommendation_test.sh pcabayes datasets/Textures/Audio/ datasets/Textures/Label/renato_join_in.txt datasets/Textures/Label/renato_join_out.txt

echo "Musician M3"
scripts/recommendation_test.sh pcabayes datasets/Textures/Audio/ datasets/Textures/Label/gabriel_in.txt datasets/Textures/Label/gabriel_out.txt
