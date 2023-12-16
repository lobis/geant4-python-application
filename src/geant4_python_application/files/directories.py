from __future__ import annotations

import os
import pathlib
import tempfile

import platformdirs

import geant4_python_application

_app_name = geant4_python_application.__name__
# TODO: get from pyproject.toml
_app_author = "lobis"

_dirs = platformdirs.AppDirs(_app_name, _app_author)

_application_directory = _dirs.user_data_dir


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
