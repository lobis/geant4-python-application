"""Point a repaired wheel's Qt dependencies at the Qt shipped in PyQt5-Qt5.

Run after delocate-wheel / auditwheel repair, which must be told to leave Qt
out of the wheel (``--exclude``). Every bundled binary that links Qt gets an
rpath to site-packages/PyQt5/Qt5/lib; on macOS any absolute Qt framework paths
(e.g. Homebrew's /opt/homebrew/opt/qt@5/...) are first rewritten to @rpath.
A marker file tells the package to use that Qt's plugins at runtime.

    python tools/relink_qt_wheel.py dist/repaired/pkg.whl -w dist/final
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = "geant4_python_application"
MARKER = f"{PACKAGE}/_qt_from_pyqt5_qt5"
# Relative to site-packages, which is the root of an unpacked wheel.
QT_LIB_DIR = "PyQt5/Qt5/lib"

# Absolute (e.g. Homebrew) or already @rpath-relative Qt framework references.
MACOS_QT_FRAMEWORK = re.compile(r"^\s+(\S*/(Qt\w+\.framework/Versions/5/Qt\w+))\s")
LINUX_QT_LIBRARY = re.compile(r"^libQt5\w+\.so\.5$")
BUNDLED_QT = re.compile(r"^(libQt5\w*|Qt[A-Z]\w*)([.-]|$)")


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def binaries(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and (path.suffix in {".so", ".dylib"} or ".so." in path.name):
            yield path


def rpath_to_qt(root: Path, binary: Path, origin: str) -> str:
    return f"{origin}/{os.path.relpath(root / QT_LIB_DIR, binary.parent)}"


def relink_macos(root: Path, binary: Path) -> bool:
    load_commands = run("otool", "-L", str(binary)).splitlines()[1:]
    references = [m.groups() for line in load_commands if (m := MACOS_QT_FRAMEWORK.match(line))]
    if not references:
        return False
    for old, framework in references:
        if old != f"@rpath/{framework}":
            run("install_name_tool", "-change", old, f"@rpath/{framework}", str(binary))
    rpath = rpath_to_qt(root, binary, "@loader_path")
    rpaths = re.findall(r"^\s+path (\S+) \(offset", run("otool", "-l", str(binary)), re.M)
    # Absolute rpaths only point into the build machine (e.g. its Qt or Geant4).
    for stale in (p for p in rpaths if p.startswith("/")):
        run("install_name_tool", "-delete_rpath", stale, str(binary))
    if rpath not in rpaths:
        run("install_name_tool", "-add_rpath", rpath, str(binary))
    # install_name_tool invalidates the ad-hoc signature, and arm64 macOS
    # refuses to load unsigned code.
    run("codesign", "--force", "--sign", "-", str(binary))
    return True


def relink_linux(root: Path, binary: Path) -> bool:
    needed = run("patchelf", "--print-needed", str(binary)).split()
    if not any(LINUX_QT_LIBRARY.match(name) for name in needed):
        return False
    entries = [e for e in run("patchelf", "--print-rpath", str(binary)).strip().split(":") if e]
    rpath = rpath_to_qt(root, binary, "$ORIGIN")
    if rpath not in entries:
        run("patchelf", "--set-rpath", ":".join([*entries, rpath]), str(binary))
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("wheel", type=Path, help="wheel already repaired by delocate/auditwheel")
    parser.add_argument("-w", "--wheel-dir", type=Path, required=True, help="output directory")
    args = parser.parse_args()

    relink = relink_macos if sys.platform == "darwin" else relink_linux
    with tempfile.TemporaryDirectory() as tmp:
        run(sys.executable, "-m", "wheel", "unpack", str(args.wheel), "-d", tmp)
        (root,) = Path(tmp).iterdir()

        bundled = [str(p.relative_to(root)) for p in root.rglob("*") if BUNDLED_QT.match(p.name)]
        if bundled:
            sys.exit(f"Qt was bundled into the wheel; exclude it during repair: {bundled}")

        relinked = [b for b in binaries(root) if relink(root, b)]
        if not relinked:
            sys.exit("No bundled binary links Qt; was the wheel built with the viewer enabled?")

        (root / MARKER).write_text("PyQt5-Qt5\n")
        args.wheel_dir.mkdir(parents=True, exist_ok=True)
        run(sys.executable, "-m", "wheel", "pack", str(root), "-d", str(args.wheel_dir))

    for binary in relinked:
        print(f"Qt -> {QT_LIB_DIR}: {binary.relative_to(root)}")


if __name__ == "__main__":
    main()
