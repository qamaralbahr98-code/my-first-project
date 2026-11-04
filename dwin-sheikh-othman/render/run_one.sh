#!/bin/bash
# render one video (lang fmt) in 2 parallel chunks, then mux, then drop the parts
cd "$(dirname "$0")"
python3 -m so.render $1 $2 --chunk 0/2 > ../build/log_$1_$2_0.txt 2>&1 &
python3 -m so.render $1 $2 --chunk 1/2 > ../build/log_$1_$2_1.txt 2>&1 &
wait
python3 -m so.render $1 $2 --concat 2 && python3 -m so.finish $1 $2 && rm -f ../build/$1/video_$2/part*.mp4 && echo "$1 $2 finished"
