CHAMPSIM=$1
TRACEDIR=$2
RESDIR=$3

mkdir -p "$RESDIR"

run_trace() {
  name=$(basename $1 .champsimtrace.xz)
  echo "Start simulating: $name"
  $CHAMPSIM/bin/champsim --warmup-instructions 5000000 --simulation-instructions 25000000 $1 > $RESDIR/${name}.champsimtrace.log
  echo "Done: $name"
}
export -f run_trace
export CHAMPSIM RESDIR

ls $TRACEDIR/*.champsimtrace.xz | xargs -P 8 -I {} bash -c 'run_trace "$@"' _ {}

echo "All done"
grep "Simulation complete" $RESDIR/*.log
