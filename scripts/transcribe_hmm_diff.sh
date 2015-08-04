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
beta=.5
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
  target_name="${name%.spec}.mean.dec"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    note=`basename "${name}" | sed 's/^.\{4\}//;s/\.spec$//'`
    ./pymir3-cl.py supervised linear decomposer mean piano "$note" "$name" /tmp/$$
    ./pymir3-cl.py supervised linear extract left /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
done

echo 'Merging basis...'
if [ ! -e "$database"/Samples/Audio/piano.mean.dec ]
then
  ./pymir3-cl.py supervised linear merge `find "$database"/Samples/Audio/Piano -name '*.mean.dec'` "$database"/Samples/Audio/piano.mean.dec
fi

echo 'Computing activations...'
for name in `find "$database"/Pieces/Audio -name '*.spec'`
do
  target_name="${name%.spec}.mean.dec"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    ./pymir3-cl.py supervised linear decomposer beta_nmf --beta $beta --basis "$database"/Samples/Audio/piano.mean.dec "$name" /tmp/$$
    ./pymir3-cl.py supervised linear extract right /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
done

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

echo 'Detecting using HMM...'
for name in `find "$database"/Pieces/Audio -name '*.mean.dec'`
do
  echo "Working with $name"
  score_name=`echo "${name%.mean.dec}.score" | sed 's,/Audio/,/Labels/Piano/,'`
  target_name1="$name.HMM.bdec"
  if [ ! -e "$target_name1" ]
    then
      ./pymir3-cl.py unsupervised detection hmm detect-diff 0.1 "$name" "$target_name1"
  fi

  target_name2="$target_name1.score"
  if [ ! -e "$target_name2" ]
  then
    ./pymir3-cl.py unsupervised detection score piano "$target_name1" /tmp/$$
    ./pymir3-cl.py tool trim_score --minimum-duration $minimum_note_length /tmp/$$ "$target_name2"
    rm /tmp/$$
  fi

  target_name3="$target_name2.symbolic.eval"
  if [ ! -e "$target_name3" ]
  then
    ./pymir3-cl.py evaluation mirex_symbolic "$target_name2" "$score_name" "$target_name3" --id "HMM"
  fi

done

echo "Finished everything! Evaluating..."
evaluations=`find "$database"/Pieces/Audio/ -name "*HMM.bdec.score.symbolic.eval"`
echo $evaluations
./pymir3-cl.py info evaluation_csv $evaluations
./pymir3-cl.py info evaluation_statistics $evaluations
