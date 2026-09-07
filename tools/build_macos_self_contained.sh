#!/bin/sh
set -eu

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This script builds the self-contained macOS wheel." >&2
    exit 2
fi

python_bin=${PYTHON:-python}
geant4_dir=${Geant4_DIR:-/usr/local/lib/cmake/Geant4}
output_dir=${1:-dist/self-contained}
raw_dir="$output_dir/raw"
repaired_dir="$output_dir/repaired"

mkdir -p "$raw_dir" "$repaired_dir"
"$python_bin" -m pip install --quiet build delocate
"$python_bin" -m build --wheel --outdir "$raw_dir" \
    -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON \
    -Ccmake.define.Geant4_DIR="$geant4_dir"

wheel=$(find "$raw_dir" -maxdepth 1 -name '*.whl' -print | head -n 1)
if [ -z "$wheel" ]; then
    echo "Wheel build did not produce an artifact." >&2
    exit 1
fi

# Homebrew builds Qt as macOS frameworks. Flattening those framework binaries
# into a wheel makes QLibraryInfo crash during GUI startup, so preserve Qt's
# framework paths while bundling Geant4, Xerces-C, Expat and other dylibs.
"$python_bin" -m delocate.cmd.delocate_wheel \
    --exclude "/qt@5/" -w "$repaired_dir" "$wheel"
echo "Relocatable Geant4 wheel written to $repaired_dir (Qt 5 remains external)"
