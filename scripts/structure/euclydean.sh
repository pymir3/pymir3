#!/bin/bash
set -o errexit

if [ $# -lt 4 ]
then
  echo "Usage: $0 <wave file> <structure start time> <structure end time> <output_figure_name>"
  exit 1
fi

echo ./pymir3-cl.py tool wav2spectrogram $1 /tmp/$$.spec
./pymir3-cl.py tool wav2spectrogram $1 /tmp/$$.spec

echo ./pymir3-cl.py info any /tmp/$$.spec
./pymir3-cl.py info any /tmp/$$.spec -m

feature_files=""
for feature in energy mfcc centroid flatness flux rolloff
do
echo "Computing $feature"
echo ./pymir3-cl.py features $feature /tmp/$$.spec /tmp/$$.$feature
./pymir3-cl.py features $feature /tmp/$$.spec /tmp/$$.$feature
featurefiles=$featurefiles" /tmp/$$.$feature"
done

echo "Joining features"
./pymir3-cl.py features join $featurefiles /tmp/$$.features.join

echo "Calculating textural similarities"
./pymir3-cl.py structure texture /tmp/$$.features.join -s $2 -e $3 > $4


