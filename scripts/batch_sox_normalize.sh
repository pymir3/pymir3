
directory=$1

for f in `ls $directory`
do
  fname=$directory/$f
sox $fname -b 16 channels 1 rate 44100 norm /tmp/$$.wav
rm $fname
mv /tmp/$$.wav $fname
done

