#!/bin/bash
set -o errexit

filename=datasets/StructureDemo/nomosalpha.wav

echo ./pymir3-cl.py tool wav2spectrogram $filename /tmp/$$.spec
./pymir3-cl.py tool wav2spectrogram $filename /tmp/$$.spec

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
./pymir3-cl.py structure pcabayes /tmp/$$.features.join -s 9.6 -e 13.3 \
  -s 27 -e 30 > xenakis1.dat

./pymir3-cl.py structure pcabayes /tmp/$$.features.join -s 27 -e 30 \
  -s 55.3 -e 58.30 > xenakis2.dat


