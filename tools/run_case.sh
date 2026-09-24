#!/bin/bash
# Mesh and solve one generated case.  Usage: tools/run_case.sh cases/fn0316 [nproc]
set -e
CASE=${1:?usage: run_case.sh <case dir> [nproc]}
NP=${2:-20}
cd "$CASE"

log() { echo "[$(date +%H:%M:%S)] $*"; }

# The conda build hard-codes an RPATH to the dummy (serial) Pstream, so
# LD_LIBRARY_PATH cannot override it -- preload the real MPI one instead.
export FOAM_PRELOAD="$CONDA_PREFIX/lib/libOpenFOAM.so $CONDA_PREFIX/lib/mpich-3.3/libPstream.so"

log "surfaceFeatureExtract"
surfaceFeatureExtract > log.surfaceFeatureExtract 2>&1

log "blockMesh"
blockMesh > log.blockMesh 2>&1

# anisotropic refinement of the free-surface band, one pass per topoSetDict
for d in system/topoSetDict.*; do
    i=${d##*.}
    topoSet -dict "$d" > "log.topoSet.$i" 2>&1
    refineMesh -dict system/refineMeshDict -overwrite > "log.refineMesh.$i" 2>&1
done

log "snappyHexMesh"
snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
checkMesh -writeFields '(nonOrthoAngle)' > log.checkMesh 2>&1 || true

rm -rf 0 && cp -r 0.orig 0
log "setFields"
setFields > log.setFields 2>&1

log "decomposePar"
decomposePar -force > log.decomposePar 2>&1

log "interFoam on $NP ranks"
LD_PRELOAD="$FOAM_PRELOAD" mpirun -np "$NP" interFoam -parallel > log.interFoam 2>&1

log "reconstructPar (last time only)"
reconstructPar -latestTime > log.reconstructPar 2>&1 || true
log "done"
