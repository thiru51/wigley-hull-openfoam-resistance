#!/bin/bash
# Run the Froude-number sweep, two cases at a time.
#
#   tools/sweep.sh            # the whole sweep
#
# Each case is generated, meshed and solved independently, so a failure in one
# leaves the others alone and the queue can be resumed by re-running.
set -u
cd "$(dirname "$0")/.."
ROOT=$PWD
ITERS=${ITERS:-1200}
NP=${NP:-10}
LEVEL=${LEVEL:-medium}

run_one() {
    local fn=$1 level=$2 tag=$3
    local case="cases/$tag"
    if [ -f "$case/DONE" ]; then echo "skip $tag (done)"; return 0; fi
    python tools/gen_case.py --fn "$fn" --level "$level" --out "$case" --iters "$ITERS" --procs "$NP" > /dev/null
    if bash tools/run_case.sh "$case" "$NP" > "$case.runlog" 2>&1; then
        touch "$case/DONE"
        echo "done $tag"
    else
        echo "FAILED $tag (see $case.runlog)"
    fi
}

export -f run_one
export ITERS NP

# Froude numbers, most informative first: the hump, the hollow, then the rest
QUEUE=(
    "0.316 $LEVEL fn0316"
    "0.250 $LEVEL fn0250"
    "0.300 $LEVEL fn0300"
    "0.350 $LEVEL fn0350"
    "0.400 $LEVEL fn0400"
    "0.280 $LEVEL fn0280"
    "0.316 coarse  fn0316_coarse"
    "0.316 fine    fn0316_fine"
)

i=0
while [ $i -lt ${#QUEUE[@]} ]; do
    a=(${QUEUE[$i]})
    b=(${QUEUE[$((i+1))]:-})
    run_one "${a[0]}" "${a[1]}" "${a[2]}" &
    p1=$!
    if [ ${#b[@]} -gt 0 ]; then run_one "${b[0]}" "${b[1]}" "${b[2]}" & p2=$!; else p2=""; fi
    wait $p1 ${p2:-}
    i=$((i+2))
done
echo "sweep finished"
