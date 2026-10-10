"""CI check that an installed wheel's Qt viewer works with the Qt from the gui extra.

Needs a display: run directly on macOS, under ``xvfb-run`` on Linux.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import textwrap

import geant4_python_application as g4

VIEWER_SECONDS = 45

if not g4.Application.visualization_available():
    sys.exit("Qt viewer unavailable: viewer module missing or the [gui] extra not installed")

# The viewer module must resolve every Qt library it links against.
subprocess.run(
    [sys.executable, "-c", "from geant4_python_application import _geant4_vis"],
    check=True,
)
print("viewer module loads")

# Open the viewer; it blocks until its window is closed, so surviving the
# timeout means the window came up and stayed up.
viewer = subprocess.Popen(
    [
        sys.executable,
        "-c",
        textwrap.dedent(
            """
            import geant4_python_application as g4
            with g4.Application(gdml=g4.basic_gdml, seed=1) as app:
                app.visualize()
            """
        ),
    ],
    # Own process group, so the Geant4 child process is cleaned up too.
    start_new_session=True,
)
try:
    viewer.wait(timeout=VIEWER_SECONDS)
except subprocess.TimeoutExpired:
    print(f"viewer still running after {VIEWER_SECONDS} s")
else:
    sys.exit(f"viewer exited early with code {viewer.returncode}")
finally:
    os.killpg(viewer.pid, signal.SIGKILL)
    viewer.wait()
