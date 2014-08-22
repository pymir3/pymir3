#!/bin/bash
set -o errexit

if [ $# -lt 1 ]
then
  echo "Usage: $0 <wave file>"
  exit 1
fi

./pymir3-cl.py tool wav2spectrogram $1 /tmp/$$

feature_files=""
for feature in energy mfcc centroid flatness flux rolloff
do
echo "Computing $feature"
./pymir3-cl.py features $feature /tmp/$$ /tmp/$$.$feature
featurefiles=$featurefiles" /tmp/$$.$feature"
done

echo "Joining features"
./pymir3-cl.py features join $featurefiles /tmp/$$.features.join

echo "Calculating mean and variance - output in CSV"
./pymir3-cl.py features stats /tmp/$$.features.join -m -v -c
