
directory=$1

for f in `ls $directory`
do
  fname=$directory/$f
  mpg123 -w $fname.wav $fname
  sox $fname.wav -b 16 -c 1 -r 44100 $fname norm
#rm $fname
#mv /tmp/$$.wav $fname
done

