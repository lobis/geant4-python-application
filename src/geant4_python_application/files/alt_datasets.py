from __future__ import annotations

import concurrent.futures
import os
import shutil
import tarfile
import tempfile
from collections import namedtuple
from pathlib import Path

import requests
from tqdm import tqdm

import geant4_python_application  # Assumes this is your module

# Dataset structure definition with necessary attributes
Dataset = namedtuple("Dataset", ["name", "version", "url", "env"])

# List of all Geant4 datasets and their download links
datasets = (
    Dataset(name="G4NDL", version="4.7.1", url="https://cern.ch/geant4-data/datasets/G4NDL.4.7.1.tar.gz", env="G4NEUTRONHPDATA"),
    Dataset(name="G4EMLOW", version="8.5", url="https://cern.ch/geant4-data/datasets/G4EMLOW.8.5.tar.gz", env="G4LEDATA"),
    Dataset(name="PhotonEvaporation", version="5.7", url="https://cern.ch/geant4-data/datasets/G4PhotonEvaporation.5.7.tar.gz", env="G4LEVELGAMMADATA"),
    Dataset(name="RadioactiveDecay", version="5.6", url="https://cern.ch/geant4-data/datasets/G4RadioactiveDecay.5.6.tar.gz", env="G4RADIOACTIVEDATA"),
    Dataset(name="G4PARTICLEXS", version="4.0", url="https://cern.ch/geant4-data/datasets/G4PARTICLEXS.4.0.tar.gz", env="G4PARTICLEXSDATA"),
    Dataset(name="G4PII", version="1.3", url="https://cern.ch/geant4-data/datasets/G4PII.1.3.tar.gz", env="G4PIIDATA"),
    Dataset(name="RealSurface", version="2.2", url="https://cern.ch/geant4-data/datasets/G4RealSurface.2.2.tar.gz", env="G4REALSURFACEDATA"),
    Dataset(name="G4SAIDDATA", version="2.0", url="https://cern.ch/geant4-data/datasets/G4SAIDDATA.2.0.tar.gz", env="G4SAIDXSDATA"),
    Dataset(name="G4ABLA", version="3.3", url="https://cern.ch/geant4-data/datasets/G4ABLA.3.3.tar.gz", env="G4ABLADATA"),
    Dataset(name="G4INCL", version="1.2", url="https://cern.ch/geant4-data/datasets/G4INCL.1.2.tar.gz", env="G4INCLDATA"),
    Dataset(name="G4ENSDFSTATE", version="2.3", url="https://cern.ch/geant4-data/datasets/G4ENSDFSTATE.2.3.tar.gz", env="G4ENSDFSTATEDATA"),
    Dataset(name="G4TENDL", version="1.4", url="https://cern.ch/geant4-data/datasets/G4TENDL.1.4.tar.gz", env="G4TENDLDATA"),
)

# Function to determine the data directory dynamically
def data_directory() -> str:
    return os.path.join(
        geant4_python_application.application_directory(),
        geant4_python_application.__name__,
        "geant4",
        geant4_python_application.geant4_version,
        "data",
    )

# Check if a dataset is already installed
def is_dataset_installed(dataset: Dataset) -> bool:
    dataset_path = os.path.join(data_directory(), f"{dataset.name}.{dataset.version}")
    return os.path.exists(dataset_path) and os.path.isdir(dataset_path)

# Get the size of the dataset for progress tracking
def _get_dataset_download_size(dataset: Dataset) -> int:
    r = requests.head(dataset.url)
    r.raise_for_status()
    return int(r.headers.get("content-length", 0))

# Get the total download size for all selected datasets
def _get_total_download_size(datasets_to_download: list[Dataset] = datasets) -> int:
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(datasets_to_download)) as executor:
        futures = [executor.submit(_get_dataset_download_size, dataset) for dataset in datasets_to_download]
        return sum(f.result() for f in concurrent.futures.as_completed(futures))

# Download and extract the dataset with progress tracking
def _download_extract_dataset(dataset: Dataset, pbar: tqdm):
    r = requests.get(dataset.url, stream=True)
    r.raise_for_status()

    chunk_size = 1024
    with tempfile.TemporaryFile() as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            pbar.update(chunk_size)

        f.seek(0)
        with tarfile.open(fileobj=f, mode="r:gz") as tar:
            tar.extractall(data_directory())

# Main function to handle the installation of datasets
def install_datasets(force: bool = False, show_progress: bool = True):
    os.environ["GEANT4_DATA_DIR"] = data_directory()
    datasets_to_download = []
    
    # Check if datasets are already downloaded, unless force is True
    for dataset in datasets:
        dataset_path = os.path.join(data_directory(), f"{dataset.name}.{dataset.version}")
        os.environ[dataset.env] = dataset_path
        if not is_dataset_installed(dataset) or force:
            datasets_to_download.append(dataset)

    if len(datasets_to_download) == 0:
        print("All datasets are already installed.")
        return  # All datasets are already installed

    os.makedirs(data_directory(), exist_ok=True)
    
    # Show progress for the dataset download and extraction
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
                for dataset in datasets_to_download
            ]
            concurrent.futures.wait(futures)

    if show_progress:
        total_size_gb = sum(
            fp.stat().st_size for fp in Path(data_directory()).rglob("*")
        ) / (1024**3)
        print(f"Geant4 datasets size on disk after extraction: {total_size_gb:.2f}GB")

# Uninstall datasets (remove the dataset directory)
def uninstall_datasets():
    dir_to_remove = os.path.dirname(data_directory())
    package_dir = os.path.dirname(__file__)

    if not os.path.relpath(package_dir, dir_to_remove).startswith(".."):
        raise RuntimeError(
            f"Refusing to remove {dir_to_remove} because it is not a subdirectory of {package_dir}"
        )
    shutil.rmtree(dir_to_remove, ignore_errors=True)

# Reinstall datasets (uninstall first, then reinstall)
def reinstall_datasets():
    uninstall_datasets()
    install_datasets(force=True)
