# Currently does not work

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.1"

ext_modules = [
    Pybind11Extension(
        "geant4_cpp",
        sources=["src/python/module.cpp"],
        include_dirs=["include"],  # Add any necessary include directories
        define_macros=[("VERSION_INFO", __version__)],
        library_dirs=["lib"],  # Add the library directory
        runtime_library_dirs=["lib"],  # Add the runtime library directory
        libraries=["geant4_cpp"],  # Add the name of your library
    ),
]

setup(
    name="geant4_cpp",
    version=__version__,
    ext_modules=ext_modules,
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
