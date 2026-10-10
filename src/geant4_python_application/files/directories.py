from __future__ import annotations

import os
import pathlib
import sys
import tempfile

import platformdirs

import geant4_python_application

_app_name = geant4_python_application.__name__
# TODO: get from pyproject.toml
_app_author = "lobis"

_dirs = platformdirs.AppDirs(_app_name, _app_author)

# Keep datasets with the active Python environment by default.  This makes a
# venv/conda installation relocatable as one unit instead of silently sharing
# data from the user's global Application Support directory.  The environment
# variable retains an explicit deployment-time override.
_application_directory = os.environ.get(
    "GEANT4_PYTHON_APPLICATION_DIR",
    os.path.join(sys.prefix, "share", _app_name),
)


def application_directory(path: str | None = None, *, temp: bool = False) -> str:
    global _application_directory

    if temp and path:
        raise ValueError("Cannot set both temp and path options")
    if temp:
        _application_directory = tempfile.gettempdir()
        return _application_directory
    if path:
        # override the default application directory
        # make sure path exists, otherwise create it. Throw if it cannot be created
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        if not os.path.isdir(path):
            raise ValueError(f"Cannot create application directory: {path}")
        _application_directory = path

    return _application_directory
