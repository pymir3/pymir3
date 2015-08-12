#!/bin/bash
set -o errexit

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

min_freq=10
max_freq=5000
window_length=2048
dft_length=4096
beta=0.5
n_tests=10
minimum_note_length=0.05

echo 'Converting wav to spectrograms...'
for name in `find "$database" -name '*.wav'`
do
  target_name="${name%.wav}.spec"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    ./pymir3-cl.py tool wav2spectrogram -l $window_length -L $dft_length "$name" /tmp/$$
    ./pymir3-cl.py tool trim_spectrogram -f $min_freq -F $max_freq /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
done

echo 'Converting samples spectrogram to basis...'
for name in `find "$database"/Samples/Audio/Piano -name '*.spec'`
do
  target_name="${name%.spec}.beta.dec"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    note=`basename "${name}" | sed 's/^.\{4\}//;s/\.spec$//'`
    ./pymir3-cl.py supervised linear decomposer beta_nmf -s 1 piano "$note" "$name" /tmp/$$
    ./pymir3-cl.py supervised linear extract left /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
done

echo 'Merging basis...'
if [ ! -e "$database"/Samples/Audio/piano.beta.dec ]
then
  ./pymir3-cl.py supervised linear merge `find "$database"/Samples/Audio/Piano  -name '*.beta.dec'` "$database"/Samples/Audio/piano.beta.dec
fi

echo 'Converting labels...'
for name in `find "$database"/Pieces/Labels/Piano -name '*.txt'`
do
  target_name="${name%.txt}.score"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    ./pymir3-cl.py tool label2score --instrument piano "$name" "$target_name"
  fi
done

echo 'Processing each individual piece...'
for name in `find "$database"/Pieces/Audio -name '*.spec'`
do
    echo $name
    echo "Computing activation"
    basename="${name%.spec}"
    target_name="${name%.spec}.beta.dec"
    if [ ! -e "$target_name" ]
    then
      ./pymir3-cl.py supervised linear decomposer beta_nmf --beta $beta --basis  "$database"/Samples/Audio/piano.beta.dec "$name" /tmp/$$
      ./pymir3-cl.py supervised linear extract right /tmp/$$ "$target_name"
      rm /tmp/$$
    fi

    echo 'Computing threshold values to test...'
    thresholds=`./pymir3-cl.py unsupervised detection threshold tests -n  $n_tests "$basename"*.beta.dec`
    echo $thresholds

    echo 'Applying thresholds'

    for th in $thresholds
    do
        th_name="${basename%.beta.dec}_th_${th}.beta"
        echo $target_name $th

        target_name1="${th_name}.bdec"
        target_name2="${th_name}.bdec.score"
        if [ ! -e "$target_name1" ]
        then
            ./pymir3-cl.py unsupervised detection threshold detect $th "$target_name" "$target_name1"
        fi

        if [ ! -e "$target_name2" ]
        then
            ./pymir3-cl.py unsupervised detection score piano "$target_name1"  /tmp/$$
            ./pymir3-cl.py tool trim_score -d $minimum_note_length  /tmp/$$ "$target_name2"
        fi
    done

    scorenames=`ls $basename*.score`
    best_score=`./pymir3-cl.py unsupervised detection threshold lower_pitchclass_entropy $scorenames`
    final_target="${best_score}.selected"
    cp $best_score $final_target

    target_name3="${basename}.beta.lower_pitchclass_entropy.symbolic.eval"
    score_name=`echo "${name%.spec}.score" | sed 's,/Audio/,/Labels/Piano/,'`
    #if [ ! -e "$target_name3" ]
    #then
        ./pymir3-cl.py evaluation mirex_symbolic "$final_target" "$score_name" "$target_name3" --id $th
    #fi
    echo $target_name3
done

evaluations=`find "$database"/Pieces/Audio/ -name "*beta.lower_pitchclass_entropy.symbolic.eval"`
./pymir3-cl.py info evaluation_csv $evaluations
./pymir3-cl.py info evaluation_statistics $evaluations
