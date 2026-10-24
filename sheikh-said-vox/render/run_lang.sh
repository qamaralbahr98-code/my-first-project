#!/bin/bash
# Full build of one language after its narration is split and timed:
#   picture (2 parallel parts) -> join -> score + sound -> loudness, mux, cover.
set -e
L=$1
cd "$(dirname "$0")"
LOG=../build/$L/video/logs
mkdir -p $LOG
python3 -m vox.render $L --chunk 0/2 > $LOG/part0.log 2>&1 &
P0=$!
python3 -m vox.render $L --chunk 1/2 > $LOG/part1.log 2>&1 &
P1=$!
wait $P0 $P1
python3 -m vox.render $L --concat 2
python3 -m vox.sound $L > $LOG/sound.log 2>&1
python3 -m vox.finish $L > $LOG/finish.log 2>&1
echo "$L finished"
