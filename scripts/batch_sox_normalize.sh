
directory=$1

for f in `ls $directory/*.wav`
do
  fname=$f
  #mpg123 -w $fname.wav $fname
  sox $fname -b 16 -c 1 -r 44100 /tmp/$$.wav norm

#rm $fname
  mv /tmp/$$.wav $fname
done

