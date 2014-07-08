#!/bin/bash

database="$1"

# Only keeps wav (sound) and txt (labels)
find "$database" -not -name '*.txt' -and -not -name '*.wav' -and -type f -exec rm '{}' \+
