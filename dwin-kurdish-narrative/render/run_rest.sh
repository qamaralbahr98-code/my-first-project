#!/bin/bash
cd "$(dirname "$0")"
for j in "$@"; do set -- $j; ./run_one.sh $1 $2; rm -rf ../build/$1/video_$2/part*; done
echo ALLDONE
