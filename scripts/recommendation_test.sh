#!/bin/bash
set -o errexit

# Recommendation test using any algorithm
# Being used by Tiago F. Tavares - 2014

contains() {
  for word in $2; do
    [[ $word = $1 ]] && return 0
  done
  return 1
}

length() {
  i=0
  for item in $1; do
    i=$(($i+1))
  done
  return $i
}

algorithm=$1
database=${2%/}
input_file=$3
output_file=$4
dbase_file=$database/features.dataset

echo "Algorithms: " $algorithm
echo "Dataset: " $database
echo "Inputs: " $input_file
echo "Outputs: " $output_file

total_hits=0
queries_with_hit=0
test_number=0
# Main loop
while true; do
  test_number=$(($test_number+1))
  read -r lineA <&4
	inputs=""
	for element in $lineA;
  do
  inputs="$inputs $database/$element"
  done
  #echo $inputs


  read -r lineB <&5
  outputs=""
	for element in $lineB;
  do
  outputs="$outputs $database/$element"
  done
  #echo $outputs


  if [ -z "$lineA" -o -z "$lineB" ]; then
    break
  fi
	recom=$(./pymir3-cl.py recommendation $algorithm $dbase_file $inputs -r 3)
  
  query_size=$((0))
  total_elements=$((0))
  hits=$((0))
  #echo "Outputs: "$outputs
  for elem in $recom;
  do
  #echo $elem
  if contains $elem "$outputs"; then
    #echo "Found!"
    hits=$(($hits+1))
    total_hits=$(($total_hits+1))
  fi
  total_elements=$(($total_elements+1))
  done
  for elem in $inputs;
  do
    query_size=$(($query_size+1))
  done

  if [ "$hits" -gt "0" ]; then
	  queries_with_hit=$(($queries_with_hit+1))
  fi

	echo $test_number, $total_elements, $hits, $query_size, $total_hits, $queries_with_hit
done 4<$input_file  5<$output_file
