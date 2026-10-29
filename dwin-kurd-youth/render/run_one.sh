#!/bin/bash
# render one video (lang fmt) in 2 parallel chunks, then mux
cd "$(dirname "$0")"
python3 -m ky.render $1 $2 --chunk 0/2 > ../build/log_$1_$2_0.txt 2>&1 &
python3 -m ky.render $1 $2 --chunk 1/2 > ../build/log_$1_$2_1.txt 2>&1 &
wait
python3 -m ky.render $1 $2 --concat 2 && python3 -m ky.finish $1 $2 && echo "$1 $2 finished"
