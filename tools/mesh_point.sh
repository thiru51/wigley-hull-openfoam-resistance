#!/bin/bash
# After the sweep: the coarse-mesh point at Fn 0.316, for the mesh study.
set -u
cd "$(dirname "$0")/.."
while pgrep -f "interFoam -parallel" > /dev/null; do sleep 120; done
python tools/gen_case.py --fn 0.316 --level coarse --out cases/fn0316_coarse --iters 3000 --procs 20 > /dev/null
bash tools/run_case.sh cases/fn0316_coarse 20 > cases/fn0316_coarse.runlog 2>&1 && touch cases/fn0316_coarse/DONE
echo "coarse mesh point finished"
