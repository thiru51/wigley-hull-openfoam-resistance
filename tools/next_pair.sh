#!/bin/bash
# Waits for the two continuation runs to finish, then meshes and solves the
# remaining Froude numbers on the same medium mesh, to the same iteration count.
set -u
cd "$(dirname "$0")/.."
while pgrep -f "interFoam -parallel" > /dev/null; do sleep 60; done
for spec in "0.350 fn0350" "0.400 fn0400"; do
    set -- $spec
    python tools/gen_case.py --fn "$1" --level medium --out "cases/$2" --iters 3000 --procs 10 > /dev/null
done
bash tools/run_case.sh cases/fn0350 10 > cases/fn0350.runlog 2>&1 &
p1=$!
bash tools/run_case.sh cases/fn0400 10 > cases/fn0400.runlog 2>&1 &
p2=$!
wait $p1 $p2
echo "second pair finished"
