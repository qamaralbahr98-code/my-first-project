#!/bin/bash
# after.sh <lang> <fmt> <next_lang> <next_fmt>: wait until the <lang> <fmt> render + finish processes are gone,
# then render <next_lang> <next_fmt>. Matches the python processes by their exact argv[0..2], so it never matches itself.
cd "$(dirname "$0")"
busy() {
  ps -eo args | awk -v a="$1" -v b="$2" '($1 ~ /python3$/ && $2 == "-m" && ($3 == "so.render" || $3 == "so.finish") && $4 == a && $5 == b) {n++}
                                  ($2 ~ /run_one\.sh$/ && $3 == a && $4 == b) {n++} END {exit !(n > 0)}'
}
while busy "$1" "$2"; do sleep 20; done
echo "$1 $2 done"
rm -f "../build/$3/video_$4/"part*.mp4
./run_one.sh "$3" "$4"
