#!/bin/bash
set -o errexit
n_process=4

database=$1

if [ ! -d "$database" -o -z "$database" ]
then
  echo "'$database' isn't a directory"
  exit
fi

min_freq=10
max_freq=5000
window_length=2048
dft_length=4096
beta=0.5
n_tests=10
minimum_note_length=0.05

wav2spectrogram () {
  window_length=$0
  dft_length=$1
  min_freq=$2
  max_freq=$3
  name="$4"
  target_name="${name%.wav}.spec"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    ./pymir3-cl.py tool wav2spectrogram -l $window_length -L $dft_length "$name" /tmp/$$
    ./pymir3-cl.py tool trim_spectrogram -f $min_freq -F $max_freq /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
}

spectrogram2basis () {
  name="$0"
  target_name="${name%.spec}.mean.dec"
  if [ ! -e "$target_name" ]
  then
    echo $name
    note=`basename "${name}" | sed 's/^.\{4\}//;s/\.spec$//'`
    ./pymir3-cl.py supervised linear decomposer mean piano "$note" "$name" /tmp/$$
    ./pymir3-cl.py supervised linear extract left /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
}

merge_basis () {
  instrument_basis="$0"
  if [ ! -e "$instrument_basis" ]
  then
    echo $instrument_basis
    ./pymir3-cl.py supervised linear merge "$@" "$instrument_basis"
  fi
}

get_activation () {
  beta=$0
  samples_dec="$1"
  suffix="$2"
  name="$3"
  target_name="${name%.spec}$suffix.dec"
  if [ ! -e "$target_name" ]
  then
    echo $name $suffix
    ./pymir3-cl.py supervised linear decomposer beta_nmf --beta $beta --basis "$samples_dec" "$name" /tmp/$$
    ./pymir3-cl.py supervised linear extract right /tmp/$$ "$target_name"
    rm /tmp/$$
  fi
}

label2score () {
  name="$0"
  target_name="${name%.txt}.score"
  if [ ! -e "$target_name" ]
  then
    echo $name
    ./pymir3-cl.py tool label2score --instrument piano "$name" "$target_name"
  fi
}

binarize () {
  th=$0
  suffix="$1"
  name="$2"
  th_name="${name%.mean.dec}_th_${th}$suffix"
  target_name1="${th_name}.bdec"
  if [ ! -e "$target_name1" ]
  then
    echo binarize $name $th
    ./pymir3-cl.py unsupervised detection threshold detect $th "$name" "$target_name1"
  fi
}

detect () {
  minimum_note_length=$0
  th=$1
  suffix="$2"
  name="$3"
  th_name="${name%.mean.dec}_th_${th}$suffix"
  target_name1="${th_name}.bdec"
  target_name2="${th_name}.score"
  if [ ! -e "$target_name2" ]
  then
    echo detect $name $th
    ./pymir3-cl.py unsupervised detection score piano "$target_name1" /tmp/$$
    ./pymir3-cl.py tool trim_score --minimum-duration $minimum_note_length /tmp/$$ "$target_name2"
    rm /tmp/$$
  fi
}

evaluate () {
  th=$0
  suffix="$1"
  name="$2"
  th_name="${name%.mean.dec}_th_${th}$suffix"
  target_name2="${th_name}.score"
  target_name3="${th_name}.symbolic.eval"
  if [ ! -e "$target_name3" ]
  then
    echo evaluate $name $th
    score_name=`echo "${name%$suffix.dec}.score" | sed 's,/Audio/,/Labels/Piano/,'`
    ./pymir3-cl.py evaluation mirex_symbolic "$target_name2" "$score_name" "$target_name3" --id $th
  fi
}

select_best () {
  suffix="$0"
  name="$1"
  base_name="${name%.wav}"
  target_name="${base_name}.th.best"
  if [ ! -e "$target_name" ]
  then
    echo select best $name
    ./pymir3-cl.py unsupervised detection threshold select_best "${base_name}"_th_*${suffix}.symbolic.eval > "$target_name"
  fi
}

export -f wav2spectrogram
export -f spectrogram2basis
export -f merge_basis
export -f get_activation
export -f label2score
export -f binarize
export -f detect
export -f evaluate
export -f select_best

echo 'Converting wav to spectrograms...'
find "$database" -name '*.wav' -print0 | xargs -0 -n 1 -P $n_process bash -c 'wav2spectrogram "$@"' $window_length $dft_length $min_freq $max_freq

echo 'Converting samples spectrogram to basis...'
find "$database"/Samples/Audio/Piano -name '*.spec' -print0 | xargs -0 -n 1 -P $n_process bash -c 'spectrogram2basis "$@"'

echo 'Merging basis...'
find "$database"/Samples/Audio/Piano -name '*.mean.dec' -print0 | xargs -0 bash -c 'merge_basis "$@"' "$database"/Samples/Audio/piano.mean.dec

echo 'Computing activations...'
find "$database"/Pieces/Audio -name '*.spec' -print0 | xargs -0 -n 1 -P $n_process bash -c 'get_activation "$@"' $beta "$database"/Samples/Audio/piano.mean.dec .mean

echo 'Converting labels...'
find "$database"/Pieces/Labels/Piano -name '*.txt' -print0 | xargs -0 -n 1 -P $n_process bash -c 'label2score "$@"'

echo 'Computing threshold values to test...'
thresholds=`./pymir3-cl.py unsupervised detection threshold tests -n $n_tests "$database"/Pieces/Audio/*.mean.dec`

echo 'Applying thresholds...'
for th in $thresholds
do
  find "$database"/Pieces/Audio -name '*.mean.dec' -print0 | xargs -0 -n 1 -P $n_process bash -c 'binarize "$@"' $th .mean
  find "$database"/Pieces/Audio -name '*.mean.dec' -print0 | xargs -0 -n 1 -P $n_process bash -c 'detect "$@"' $minimum_note_length $th .mean
  find "$database"/Pieces/Audio -name '*.mean.dec' -print0 | xargs -0 -n 1 -P $n_process bash -c 'evaluate "$@"' $th .mean
done

echo 'Selecting best threshold'
final_th=`./pymir3-cl.py unsupervised detection threshold select_best "$database"/Pieces/Audio/*.mean.symbolic.eval`

echo 'Final evaluation:'
echo $final_th

evaluations=`find "$database"/Pieces/Audio/ -name "*${final_th}.mean.symbolic.eval"`
./pymir3-cl.py info evaluation_csv $evaluations
./pymir3-cl.py info evaluation_statistics $evaluations
