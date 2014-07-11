#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 <dataset directory>"
  exit 1
fi

if [ ! -d "$1" ]
then
  echo "Invalid directory \"$1\"!"
  exit 1
fi

database="$1"

# Only keeps wav (sound) and txt (labels)
find "$database" -not -name '*.txt' -and -not -name '*.wav' -and -type f -exec rm '{}' \+
