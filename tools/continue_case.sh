#!/bin/bash
# Continue a case that has already been meshed and run, to a later iteration.
#
#   tools/continue_case.sh cases/fn0316 3000 10
#
# The force history in postProcessing is appended to under a new start-time
# directory; postprocess.py reads all of them in order, so the continuation is
# invisible downstream.
set -e
CASE=${1:?usage: continue_case.sh <case dir> <end iteration> [nproc]}
END=${2:?end iteration}
NP=${3:-10}
cd "$CASE"

export FOAM_PRELOAD="$CONDA_PREFIX/lib/libOpenFOAM.so $CONDA_PREFIX/lib/mpich-3.3/libPstream.so"

foamDictionary system/controlDict -entry endTime -set "$END"
foamDictionary system/controlDict -entry startFrom -set latestTime

echo "[$(date +%H:%M:%S)] continuing $(basename "$CASE") to $END on $NP ranks"
LD_PRELOAD="$FOAM_PRELOAD" mpirun -np "$NP" interFoam -parallel >> log.interFoam 2>&1
echo "[$(date +%H:%M:%S)] done"
