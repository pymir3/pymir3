#!/bin/bash
set -o errexit


filename=$1

window_length=2048
dft_length=2048
window_step=1024

echo "Calculating spectrogram..."
spectrogram_name="${filename%.wav}.spec"
./pymir3-cl.py tool wav2spectrogram -l $window_length -L $dft_length -s $window_step -t magnitude $filename $spectrogram_name
echo "Done!"
echo "Calculating features..."

feature_file_list=""
for feature in centroid energy flux mfcc rolloff flatness
do
		feature_file="${filename%.wav}.$feature.track"
		feature_file_list="$feature_file_list $feature_file"
		if [ ! -e "$feature_file" ]
		then
				echo Calculating "$feature"
				./pymir3-cl.py features $feature $spectrogram_name $feature_file
		fi

		diff_file="${filename%.wav}.$feature.diff.track"
		feature_file_list="$feature_file_list $diff_file"
		if [ ! -e $diff_file ]
		then
				./pymir3-cl.py features diff $feature_file $diff_file
		fi

		diff2_file="${filename%.wav}.$feature.diff2.track"
		feature_file_list="$feature_file_list $diff2_file"
		if [ ! -e $diff2_file ]
		then
				./pymir3-cl.py features diff $diff_file $diff2_file
		fi
done

echo "Done!"
# Join features in a single file
echo "Joining features into a single file"
feature_track_name=${filename%.wav}.track
./pymir3-cl.py features join $feature_file_list $feature_track_name
echo "Done!"

echo "Calculating self-similarity matrix..."
self_similarity_name="${filename%.wav}.ssm"
./pymir3-cl.py features selfsimilarity $feature_track_name $self_similarity_name
echo "Done!"

