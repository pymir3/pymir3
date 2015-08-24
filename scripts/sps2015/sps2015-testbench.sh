

for database in datasets/MAPS
do
  for window in 128 256 512 1024 2048
  do
    for split in 1 3 5 7
    do
      echo $database $window $split
      sh scripts/clean.sh $database
      sh scripts/sps2015/sps2015.sh $database ${window} $split
      #sh scripts/clean.sh $database
    done
  done
done
