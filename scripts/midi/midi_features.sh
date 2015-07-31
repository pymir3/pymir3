#!/bin/sh

set -o errexit

if [ $# -lt 1 ]
then
  echo "Usage: $0 <midi file>"
  exit 1
fi

echo ./pymir3-cl.py tool midi2score $1 /tmp/$$.score
./pymir3-cl.py tool midi2score 0 $1 /tmp/$$.score


feats=''
for feature in density intervals pitchclass range relativerange rhythm
do
  thisfeat=`./pymir3-cl.py symbolic $feature /tmp/$$.score`
  feats=`echo $feats $thisfeat`
done

echo $feats
