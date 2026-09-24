#!/bin/bash
# Runs after the sweep: a low-speed case where wave making is negligible, so
# the pressure resistance it reports is the form + numerical floor that every
# other case also carries.  Cp(Fn) - Cp(0.10) is then the wave-making part.
set -u
cd "$(dirname "$0")/.."
until grep -q "sweep finished" sweep.log 2>/dev/null; do sleep 60; done
python tools/gen_case.py --fn 0.10 --level medium --out cases/fn0100 --iters 1200 --procs 20 > /dev/null
bash tools/run_case.sh cases/fn0100 20 > cases/fn0100.runlog 2>&1 && touch cases/fn0100/DONE
echo "baseline finished"
