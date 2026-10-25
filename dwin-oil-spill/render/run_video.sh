#!/bin/bash
# Render the silent picture for one language and format: two parallel parts, then join.
#   bash run_video.sh ckb 16x9
set -e
cd "$(dirname "$0")"
L=$1; F=$2
python3 -m oil.render $L $F --chunk 0/2 > ../build/$L/render_${F}_0.log 2>&1 &
P0=$!
python3 -m oil.render $L $F --chunk 1/2 > ../build/$L/render_${F}_1.log 2>&1 &
P1=$!
wait $P0; wait $P1
python3 -m oil.render $L $F --concat 2
echo "$L $F picture done"
