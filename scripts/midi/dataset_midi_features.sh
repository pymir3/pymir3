#!/bin/bash
set -o errexit

# Gets features from a directory of midi files.


database=${1%/}

outputfile=$2

if [ ! -d "$database" -o -z "$database" ]
then
  echo "'$database' isn't a directory"
  exit
fi

for name in `find "$database" -name '*.mid'`
do
    #echo ./pymir3-cl.py tool midi2score 1 $name /tmp/$$.score
    ./pymir3-cl.py tool midi2score 1 $name /tmp/$$.score


    feats=$name
    for feature in density intervals pitchclass range relativerange rhythm
    do
        tag=""
        if [ "$feature" = "intervals" ] | [ "$feature" = "pitchclass" ]
        then
            tag=" -s "
        fi

    thisfeat=`./pymir3-cl.py symbolic $feature $tag /tmp/$$.score`
    feats=`echo $feats $thisfeat`
    done

    echo $feats
done


