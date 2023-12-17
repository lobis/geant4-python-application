from __future__ import annotations

import concurrent.futures
import hashlib
import os
import shutil
import tarfile
import tempfile
from collections import namedtuple
from pathlib import Path

import requests
from tqdm import tqdm

import geant4_python_application

url = "https://cern.ch/geant4-data/datasets"


# It is discouraged to use the package directory to store data
# data_dir = os.path.join(os.path.dirname(__file__), "geant4/data")
# another idea is to use 'platformdirs' to store data in a platform-specific location


def data_directory() -> str:
    return os.path.join(
        geant4_python_application.application_directory(),
        geant4_python_application.__name__,
        "geant4",
        geant4_python_application.geant4_version,
        "data",
    )


# the datasets versions should be updated with each Geant4 version
# https://geant4.web.cern.ch/download/11.2.0.html#datasets
Dataset = namedtuple("Dataset", ["name", "version", "filename", "env", "md5sum"])

datasets = (
    Dataset(
        name="G4NDL",
        version="4.7",
        filename="G4NDL",
        env="G4NEUTRONHPDATA",
        md5sum="b001a2091bf9392e6833830347672ea2",
    ),
    Dataset(
        name="G4EMLOW",
        version="8.5",
        filename="G4EMLOW",
        env="G4LEDATA",
        md5sum="146d0625d8d39f294056e1618271bc46",
    ),
    Dataset(
        name="PhotonEvaporation",
        version="5.7",
        filename="G4PhotonEvaporation",
        env="G4LEVELGAMMADATA",
        md5sum="81ff27deb23af4aa225423e6b3a06b39",
    ),
    Dataset(
        name="RadioactiveDecay",
        version="5.6",
        filename="G4RadioactiveDecay",
        env="G4RADIOACTIVEDATA",
        md5sum="acc1dbeb87b6b708b2874ced729a3a8f",
    ),
    Dataset(
        name="G4PARTICLEXS",
        version="4.0",
        filename="G4PARTICLEXS",
        env="G4PARTICLEXSDATA",
        md5sum="d82a4d171d50f55864e28b6cd6f433c0",
    ),
    Dataset(
        name="G4PII",
        version="1.3",
        filename="G4PII",
        env="G4PIIDATA",
        md5sum="05f2471dbcdf1a2b17cbff84e8e83b37",
    ),
    Dataset(
        name="RealSurface",
        version="2.2",
        filename="G4RealSurface",
        env="G4REALSURFACEDATA",
        md5sum="ea8f1cfa8d8aafd64b71fb30b3e8a6d9",
    ),
    Dataset(
        name="G4SAIDDATA",
        version="2.0",
        filename="G4SAIDDATA",
        env="G4SAIDXSDATA",
        md5sum="d5d4e9541120c274aeed038c621d39da",
    ),
    Dataset(
        name="G4ABLA",
        version="3.3",
        filename="G4ABLA",
        env="G4ABLADATA",
        md5sum="b25d093339e1e4532e31038653580ca6",
    ),
    Dataset(
        name="G4INCL",
        version="1.2",
        filename="G4INCL",
        env="G4INCLDATA",
        md5sum="0a76df936839bb557dae7254117eb58e",
    ),
    Dataset(
        name="G4ENSDFSTATE",
        version="2.3",
        filename="G4ENSDFSTATE",
        env="G4ENSDFSTATEDATA",
        md5sum="6f18fce8f217e7aaeaa3711be9b2c7bf",
    ),
)


def _dataset_url(dataset: Dataset) -> str:
    return f"{url}/{dataset.filename}.{dataset.version}.tar.gz"


def _get_dataset_download_size(dataset: Dataset) -> int:
    r = requests.head(_dataset_url(dataset))
    r.raise_for_status()
    return int(r.headers.get("content-length", 0))


def _get_total_download_size(datasets_to_download: list[Dataset] = datasets) -> int:
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(datasets_to_download)
    ) as executor:
        futures = [
            executor.submit(_get_dataset_download_size, dataset)
            for dataset in datasets_to_download
        ]
        return sum(f.result() for f in concurrent.futures.as_completed(futures))


def _download_extract_dataset(dataset: Dataset, pbar: tqdm):
    filename = dataset.filename
    urlpath = f"{url}/{filename}.{dataset.version}.tar.gz"
    r = requests.get(urlpath, stream=True)
    r.raise_for_status()

    chunk_size = 1024
    with tempfile.TemporaryFile() as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            pbar.update(chunk_size)

        f.seek(0)
        md5 = hashlib.md5()
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5.update(chunk)
        if md5.hexdigest() != dataset.md5sum:
            raise RuntimeError(f"MD5 checksum mismatch for {filename}")

        f.seek(0)
        with tarfile.open(fileobj=f, mode="r:gz") as tar:
            tar.extractall(data_directory())


def install_datasets(force: bool = False, show_progress: bool = True):
    os.environ["GEANT4_DATA_DIR"] = data_directory()
    datasets_to_download = []
    for dataset in datasets:
        path = os.path.join(data_directory(), dataset.name + dataset.version)
        os.environ[dataset.env] = path
        if not os.path.exists(path) or force:
            datasets_to_download.append(dataset)

    if len(datasets_to_download) == 0:
        return

    os.makedirs(data_directory(), exist_ok=True)
    if show_progress:
        print(
            f"""
Geant4 datasets (<2GB) will be installed to "{data_directory()}".
This may take a while but only needs to be done once.
You can override the default location by calling `application_directory(path)` or `application_directory(temp=True)` to use a temporary directory.
The following Geant4 datasets will be installed: {", ".join([f"{dataset.name}@v{dataset.version}" for dataset in datasets_to_download])}"""
        )

    with tqdm(
        total=_get_total_download_size(datasets_to_download),
        desc="Downloading Geant4 datasets",
        disable=not show_progress,
        unit="B",
        unit_scale=True,
    ) as pbar:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(datasets_to_download)
        ) as executor:
            futures = [
                executor.submit(_download_extract_dataset, dataset, pbar)
                for i, dataset in enumerate(datasets_to_download)
            ]
            concurrent.futures.wait(futures)

    if show_progress:
        total_size_gb = sum(
            fp.stat().st_size for fp in Path(data_directory()).rglob("*")
        ) / (1024**3)
        print(f"Geant4 datasets size on disk after extraction: {total_size_gb:.2f}GB")


def uninstall_datasets():
    dir_to_remove = os.path.dirname(data_directory())
    package_dir = os.path.dirname(__file__)

    if not os.path.relpath(package_dir, dir_to_remove).startswith(".."):
        # make sure we don't accidentally delete something important
        raise RuntimeError(
            f"Refusing to remove {dir_to_remove} because it is not a subdirectory of {package_dir}"
        )
    shutil.rmtree(dir_to_remove, ignore_errors=True)


def reinstall_datasets():
    uninstall_datasets()
    install_datasets(force=True)
