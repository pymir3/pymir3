#!/bin/bash
set -o errexit

if [ $# -lt 1 ]
then
  echo "Usage: $0 <wave file>"
  exit 1
fi

echo "./pymir3-cl.py tool wav2spectrogram $1 /tmp/$$"

feature_files=""
for feature in energy mfcc centroid flatness flux rolloff
do
echo "Computing $feature"
echo "./pymir3-cl.py feature $feature /tmp/$$ /tmp/$$.$feature"
featurefiles=$featurefiles" /tmp/$$.$feature"
done

echo "Joining features"
echo "./pymir3-cl.py feature join $featurefiles /tmp/$$.features.join"

