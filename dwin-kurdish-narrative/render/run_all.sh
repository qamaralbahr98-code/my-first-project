#!/bin/bash
cd "$(dirname "$0")"
for l in ar ckb kmr; do python3 -m kn.sound $l || exit 1; done
for l in ar ckb kmr; do for f in 16x9 9x16; do ./run_one.sh $l $f; rm -rf ../build/$l/video_$f/part*; done; done
echo ALLDONE
