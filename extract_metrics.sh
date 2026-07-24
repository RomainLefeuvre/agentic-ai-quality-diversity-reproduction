#GRAPH_PATH=/mnt/data/graph/2025-05-18/
GRAPH_PATH=/mnt/data/graph/2026-06-04/
STORAGE_PATH=/srv/storage/swhresearchfoundry@storage4.nancy.grid5000.fr
RESULT_PATH="$PWD/output-fina"
TMPFS_PATH=/mnt/tmpfs_swh

RUN_ID="$(date +%Y-%m-%d)_$(git rev-parse --short HEAD)"
OUTPUT_PATH="$RESULT_PATH/$RUN_ID"
mkdir -p "$OUTPUT_PATH"

# Some graph files are moved onto tmpfs by ./python/graph_to_tmpfs.py and replaced
# with symlinks under $TMPFS_PATH/graph/<date>/. Since those symlinks are
# absolute host paths, $TMPFS_PATH must be bound into the container at the same
# path or they'll dangle.
singularity run \
  -B "$PWD":/workspace \
  -B "$GRAPH_PATH":/workspace/graph:ro \
  -B "$STORAGE_PATH":"$STORAGE_PATH":ro \
  -B "$OUTPUT_PATH":/workspace/output \
  -B "$PWD/swh-filter-target":/build/target \
  -B "$PWD/cargo-cache":/usr/local/cargo/registry \
  -B "$TMPFS_PATH":"$TMPFS_PATH" \
  docker://registry.gitlab.inria.fr/diverse/swh-filter:latest \
  --graph /workspace/graph/graph \
  --output-dir /workspace/output \
  --chunk-size 1000000 --threads 0\
  --origin-urls input/agentic_usage_swh.csv  