#!/bin/bash
set -o errexit

for name in `find . -name *.au`; do sox $name ../genres_wav/`basename $name .au`.wav; done 
