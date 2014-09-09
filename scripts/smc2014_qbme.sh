#!/bin/bash
set -o errexit


scripts/clean.sh datasets/Textures/Audio/
scripts/dataset_features.sh datasets/Textures/Audio/
scripts/recommendation_test.sh pcabayes datasets/Textures/Audio/ datasets/Textures/Label/adriano_in.txt datasets/Textures/Label/adriano_out.txt 
