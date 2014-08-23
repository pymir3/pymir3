#!/bin/bash
set -o errexit

# Gets features from a directory of wav files.
# Uses only features that are good for samples.
# (up to about 10s of audio)

database=${1%/}

window_length=1024
dft_length=1024
window_step=512

if [ ! -d "$database" -o -z "$database" ]
then
  echo "'$database' isn't a directory"
  exit
fi

# Compute spectrogram
echo 'Converting wav to spectrograms...'
for name in `find "$database" -name '*.wav'` 
#for name in $(ls -1 $database/*.wav | sort -n -k1.4)
do
  target_name="${name%.wav}.spec"
  if [ ! -e "$target_name" ]
  then
    echo "$name"
    ./pymir3-cl.py tool wav2spectrogram -l $window_length -L $dft_length -s $window_step -t magnitude $name $target_name
  fi
done

echo 'Calculating features from spectrograms...'
for name in `find "$database" -name '*.spec'`
do
  target_name="${name%.spec}.features"
  if [ ! -e $target_name ]
  then
			for feature in centroid energy flux mfcc rolloff flatness
			do
					feature_file="${name%.spec}.$feature.track"
					if [ ! -e "$feature_file" ]
					then
							echo Calculating "$feature" for "$name"
							./pymir3-cl.py features $feature $name $feature_file
					fi
			done

  # Calculate differentials
  # Join features in a single file
			diff_file="${name%.spec}.$feature.diff.track"
			if [ ! -e $diff_file ]
			then
					./pymir3-cl.py features diff $feature_file $diff_file
			fi

			diff2_file="${name%.spec}.$feature.diff2.track"
			if [ ! -e $diff2_file ]
			then
					./pymir3-cl.py features diff $diff_file $diff2_file
			fi

  # Join features in a single file
			echo "Joining features into a single file"
			./pymir3-cl.py features join `find "$database" -name '*.track'` $target_name
			rm "$database"/*.track
  fi

done

echo "Calculating statistics from all feature tracks"
final_name="$database"/features.dataset
./pymir3-cl.py features stats -m -v -s -l -n `find "$database" -name '*.features'` $final_name
#./minion.py info features $final_name


