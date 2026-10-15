from __future__ import annotations

import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
from collections import namedtuple
from pathlib import Path

import requests
from tqdm import tqdm

import geant4_python_application

url = "https://cern.ch/geant4-data/datasets"


# It is discouraged to use the python package directory to store data
# data_dir = os.path.join(os.path.dirname(__file__), "geant4/data")
# another idea is to use 'platformdirs' to store data in a platform-specific location
def application_data_directory() -> str:
    return os.path.join(
        geant4_python_application.application_directory(),
        geant4_python_application.__name__,
        "geant4",
        geant4_python_application.geant4_version,
        "data",
    )


def geant4_data_directory() -> str:
    try:
        # capture stdout, save into a str
        geant4_prefix = subprocess.run(
            ["geant4-config", "--prefix"], capture_output=True, check=False
        )
        geant4_data_path = os.path.join(
            geant4_prefix.stdout.decode().strip(), "share", "Geant4", "data"
        )
        if not os.path.exists(geant4_data_path):
            return ""

        return geant4_data_path

    except FileNotFoundError:
        return ""


def installation_datasets() -> dict[str, str]:
    """Datasets of an installed Geant4 (e.g. conda-forge) as {env var: path}.

    Uses the dataset environment variables if they are already set (conda sets
    them on activation), otherwise asks ``geant4-config --check-datasets`` where
    each one is installed. Directory names are not guessed: Geant4 11.4 installs
    e.g. ``NDL4.7.1`` rather than ``G4NDL4.7.1``. Empty unless that Geant4 is the
    version this package was built against and every dataset it needs exists.
    """
    try:
        version = subprocess.run(
            ["geant4-config", "--version"], capture_output=True, text=True, check=False
        ).stdout.strip()
    except OSError:
        version = ""
    if version != geant4_python_application.geant4_version:
        return {}

    from_environment = {
        dataset.env: os.environ[dataset.env]
        for dataset in datasets
        if os.path.isdir(os.environ.get(dataset.env, ""))
    }
    if len(from_environment) == len(datasets):
        return from_environment

    try:
        listing = subprocess.run(
            ["geant4-config", "--check-datasets"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    except OSError:
        return {}
    installed = {}
    for line in listing.splitlines():
        fields = line.split(maxsplit=2)
        if len(fields) == 3 and fields[1] == "INSTALLED" and os.path.isdir(fields[2]):
            installed[fields[0]] = fields[2]
    if not all(dataset.name in installed for dataset in datasets):
        return {}
    return {dataset.env: installed[dataset.name] for dataset in datasets}


# the datasets versions should be updated with each Geant4 version (remember to update the checksum too!)
# https://geant4.web.cern.ch/download/11.4.3.html#datasets
# (cmake/Modules/G4DatasetDefinitions.cmake; the optional TENDL, NuDEXLib and URRPT are left out)
Dataset = namedtuple("Dataset", ["name", "version", "filename", "env", "md5sum"])

datasets = (
    Dataset(
        name="G4NDL",
        version="4.7.1",
        filename="G4NDL",
        env="G4NEUTRONHPDATA",
        md5sum="54f0ed3995856f02433d42ec96d70bc6",
    ),
    Dataset(
        name="G4EMLOW",
        version="8.8",
        filename="G4EMLOW",
        env="G4LEDATA",
        md5sum="328330009df633f7e9b3a9f445745298",
    ),
    Dataset(
        name="PhotonEvaporation",
        version="6.1.2",
        filename="G4PhotonEvaporation",
        env="G4LEVELGAMMADATA",
        md5sum="d80ba9bdefcf9e23487a26adfa273304",
    ),
    Dataset(
        name="RadioactiveDecay",
        version="6.1.2",
        filename="G4RadioactiveDecay",
        env="G4RADIOACTIVEDATA",
        md5sum="20d494f73d4bddabd7fab5c06a58895c",
    ),
    Dataset(
        name="G4PARTICLEXS",
        version="4.2",
        filename="G4PARTICLEXS",
        env="G4PARTICLEXSDATA",
        md5sum="b63341cc97a472b04ff607b094493174",
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
        version="1.3",
        filename="G4INCL",
        env="G4INCLDATA",
        md5sum="72c3ff5f7f1e6f727f2ebf3b11ce784f",
    ),
    Dataset(
        name="G4ENSDFSTATE",
        version="3.0",
        filename="G4ENSDFSTATE",
        env="G4ENSDFSTATEDATA",
        md5sum="c500728534ce3e9fb2fefa0112eb3a74",
    ),
    Dataset(
        name="G4CHANNELING",
        version="2.0",
        filename="G4CHANNELING",
        env="G4CHANNELINGDATA",
        md5sum="e853fbcba1e8640f7c3a437253955482",
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


chunk_size = 1024 * 1024
max_attempts = 5


def _download_extract_dataset(dataset: Dataset, pbar: tqdm):
    filename = dataset.filename
    urlpath = _dataset_url(dataset)

    with tempfile.TemporaryFile() as f:
        downloaded = 0
        for attempt in range(max_attempts):
            # resume where the previous attempt died instead of restarting a multi-GB download
            headers = {"Range": f"bytes={downloaded}-"} if downloaded else {}
            try:
                r = requests.get(urlpath, stream=True, headers=headers, timeout=60)
                r.raise_for_status()
                if downloaded and r.status_code != 206:
                    # server ignored the range request, so start over
                    f.seek(0)
                    f.truncate()
                    pbar.update(-downloaded)
                    downloaded = 0
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    pbar.update(len(chunk))
                break
            except requests.RequestException:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2**attempt)

        f.seek(0)
        md5 = hashlib.md5()
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5.update(chunk)
        if md5.hexdigest() != dataset.md5sum:
            print(
                f"MD5 checksum mismatch for {filename}: got {md5.hexdigest()} but expected {dataset.md5sum}"
            )
            raise RuntimeError(f"MD5 checksum mismatch for {filename}")

        f.seek(0)
        with tarfile.open(fileobj=f, mode="r:gz") as tar:
            tar.extractall(application_data_directory())


def missing_datasets(directory: str) -> list[Dataset]:
    datasets_to_download = []
    for dataset in datasets:
        path = os.path.join(directory, dataset.name + dataset.version)
        if not os.path.exists(path):
            datasets_to_download.append(dataset)
    return datasets_to_download


def _reuse_from_other_versions(datasets_to_download: list[Dataset]) -> list[Dataset]:
    """Link datasets already downloaded for another Geant4 version instead of
    downloading them again (a dataset's name and version identify its content).

    Files are hard-linked, so the copy takes no extra disk space; if that is not
    possible (e.g. another filesystem) they are copied. Returns what is still missing.
    """
    target = application_data_directory()
    versions_directory = os.path.dirname(os.path.dirname(target))
    try:
        others = [
            os.path.join(versions_directory, version, "data")
            for version in os.listdir(versions_directory)
            if version != geant4_python_application.geant4_version
        ]
    except FileNotFoundError:
        return datasets_to_download

    def link_or_copy(src, dst):
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)

    still_missing = []
    for dataset in datasets_to_download:
        name = dataset.name + dataset.version
        source = next(
            (
                os.path.join(other, name)
                for other in others
                if os.path.isdir(os.path.join(other, name))
            ),
            None,
        )
        if source is None:
            still_missing.append(dataset)
            continue
        # copy into a temporary name first so an interrupted copy is never mistaken
        # for a complete dataset
        partial = os.path.join(target, name + ".partial")
        shutil.rmtree(partial, ignore_errors=True)
        shutil.copytree(source, partial, copy_function=link_or_copy)
        os.rename(partial, os.path.join(target, name))
    return still_missing


def check_datasets(throw: bool = False) -> bool:
    datasets_to_download = missing_datasets(directory=application_data_directory())
    if datasets_to_download and installation_datasets():
        # provided by the Geant4 installation (e.g. conda-forge) instead
        datasets_to_download = []

    if datasets_to_download:
        if throw:
            raise RuntimeError(
                f"Missing Geant4 datasets: {', '.join([f'{dataset.name}@v{dataset.version}' for dataset in datasets_to_download])}"
            )
        return False
    return True


def install_datasets(show_progress: bool = True):
    # first try to see if the datasets are installed in the application directory
    datasets_to_download = missing_datasets(directory=application_data_directory())
    if not datasets_to_download:
        # datasets are installed in application directory
        os.environ["GEANT4_DATA_DIR"] = application_data_directory()
        return

    installed = installation_datasets()
    if installed:
        # the Geant4 installation provides them; point Geant4 at each one
        os.environ.update(installed)
        return

    # download and extract the datasets to the application data directory
    os.environ["GEANT4_DATA_DIR"] = application_data_directory()

    os.makedirs(application_data_directory(), exist_ok=True)
    datasets_to_download = missing_datasets(directory=application_data_directory())
    datasets_to_download = _reuse_from_other_versions(datasets_to_download)
    if not datasets_to_download:
        return
    if show_progress:
        print(
            f"""
Geant4 datasets will be installed to "{application_data_directory()}".
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
            for future in concurrent.futures.as_completed(futures):
                # surface download/extraction errors instead of reporting a partial install as success
                future.result()

    if show_progress:
        total_size_gb = sum(
            fp.stat().st_size for fp in Path(application_data_directory()).rglob("*")
        ) / (1024**3)
        print(f"Geant4 datasets size on disk after extraction: {total_size_gb:.2f}GB")


def uninstall_datasets():
    dir_to_remove = os.path.dirname(application_data_directory())
    package_dir = os.path.dirname(__file__)

    if not os.path.relpath(package_dir, dir_to_remove).startswith(".."):
        raise RuntimeError(
            f"Refusing to remove {dir_to_remove} because it is not a subdirectory of {package_dir}"
        )
    shutil.rmtree(dir_to_remove, ignore_errors=True)


def reinstall_datasets():
    uninstall_datasets()
    install_datasets()
