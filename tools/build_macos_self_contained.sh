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

rm -rf "$raw_dir" "$repaired_dir"
mkdir -p "$raw_dir" "$repaired_dir" "$output_dir"
"$python_bin" -m pip install --quiet build delocate wheel
"$python_bin" -m build --wheel --outdir "$raw_dir" \
    -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON \
    -Ccmake.define.Geant4_DIR="$geant4_dir"

wheel=$(find "$raw_dir" -maxdepth 1 -name '*.whl' -print | head -n 1)
if [ -z "$wheel" ]; then
    echo "Wheel build did not produce an artifact." >&2
    exit 1
fi

# Bundle Geant4, Xerces-C, Expat and other dylibs, but leave Qt out: the wheel
# takes Qt from the PyQt5-Qt5 package (the [gui] extra) at runtime instead of
# the build machine's Qt, which relink_qt_wheel.py sets up.
"$python_bin" -m delocate.cmd.delocate_wheel \
    --exclude .framework/Versions/5/Qt -w "$repaired_dir" "$wheel"
"$python_bin" "$(dirname "$0")/relink_qt_wheel.py" "$repaired_dir"/*.whl -w "$output_dir"
rm -rf "$raw_dir" "$repaired_dir"
echo "Relocatable wheel written to $output_dir; install it with the [gui] extra for the viewer"
