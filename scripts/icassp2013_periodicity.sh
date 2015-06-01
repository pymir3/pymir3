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
exponent=1.0
beta=0.5
window_length=2048
dft_length=4096
minimum_note_length=0.05





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



echo 'Converting pieces wav to spectrograms...'
for name in `find $database/Pieces/Audio -name '*.wav'`
do
  if [ ! -e ${name%.wav}.spec ]
  then
    echo $name
    ./pymir3-cl.py tool wav2spectrogram $name /tmp/$$
    ./pymir3-cl.py tool trim_spectrogram -f $min_freq -F $max_freq /tmp/$$ ${name%.wav}.spec
  fi
done




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
for name in `find $database/Pieces/Labels/Piano -name '*.txt'`
do
  if [ ! -e ${name%.txt}.score ]
  then
    echo $name
    ./pymir3-cl.py tool label2score --instrument piano $name ${name%.txt}.score
  fi
done



for name in `find $database/Pieces/Audio -name '*.act'`
do
  score_name=`echo ${name%.act}.score | sed 's,/Audio/,/Labels/Piano/,'`
  if [ ! -e ${name%.act}.bact ]
  then
    echo $name
		echo 'Computing threshold values to test...'
    thresholds=`./pymir3-cl.py unsupervised detection threshold tests -n 100 $name`
  	echo "Looking for thresholds:"
    echo $thresholds
    th=`./pymir3-cl.py unsupervised detection threshold best_periodicity -e $exponent $name $thresholds`
	  echo "Found best threshold:"
	  echo $th
    echo "Converting..."
    score_name=`echo ${name%.act}.score | sed 's,/Audio/,/Labels/Piano/,'`
    ./pymir3-cl.py unsupervised detection threshold detect $th $name ${name%.act}.bact
  fi
  if [ ! -e ${name%.act}.pre_score ]
  then
     echo ${name%.act}.bact
    ./pymir3-cl.py unsupervised detection score piano ${name%.act}.bact ${name%.act}.pre_score
#			./minion.py tool score2label ${name%.act}_th_$th.score test.lab
#			cat test.lab
#			rm test.lab
  fi
  if [ ! -e ${name%.act}_symbolic.eval ]
  then
		./pymir3-cl.py tool trim_score --min_duration $minimum_note_length ${name%.act}.pre_score ${name%.act}.score
		./pymir3-cl.py evaluation mirex_symbolic ${name%.act}.score $score_name ${name%.act}_symbolic.eval
    ./pymir3-cl.py info evaluation ${name%.act}_symbolic.eval
  fi
	echo "----"
done

echo "=========="
./pymir3-cl.py info evaluation_csv $database/Pieces/Audio/*.eval

echo "=========="
./pymir3-cl.py info evaluation_statistics $database/Pieces/Audio/*.eval
