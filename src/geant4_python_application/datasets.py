from __future__ import annotations

import concurrent.futures
import hashlib
import os
import tarfile
import tempfile
from collections import namedtuple

import requests
import tqdm

url = "https://cern.ch/geant4-data/datasets"
data_dir = os.path.join(os.path.dirname(__file__), "geant4/data")

# https://github.com/HaarigerHarald/geant4_pybind/blob/9bc90bc7f93df0d4966f29c90ffed5655e8d5904/source/datainit.py
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
        version="8.2",
        filename="G4EMLOW",
        env="G4LEDATA",
        md5sum="07773e57be3f6f2ebb744da5ed574f6d",
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
        version="3.1",
        filename="G4ABLA",
        env="G4ABLADATA",
        md5sum="180f1f5d937733b207f8d5677f76296e",
    ),
    Dataset(
        name="G4INCL",
        version="1.0",
        filename="G4INCL",
        env="G4INCLDATA",
        md5sum="85fe937b6df46d41814f07175d3f5b51",
    ),
    Dataset(
        name="G4ENSDFSTATE",
        version="2.3",
        filename="G4ENSDFSTATE",
        env="G4ENSDFSTATEDATA",
        md5sum="6f18fce8f217e7aaeaa3711be9b2c7bf",
    ),
)


def _download_extract_dataset(dataset: Dataset, progress_bar_position: int = 0):
    filename = dataset.filename
    urlpath = f"{url}/{filename}.{dataset.version}.tar.gz"
    r = requests.get(urlpath, stream=True)
    r.raise_for_status()

    # Get the total file size for tqdm
    total_size = int(r.headers.get("content-length", 0))
    chunk_size = 4096
    with tempfile.TemporaryFile() as f, tqdm.tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        desc=f"Downloading and Extracting {filename}",
        position=progress_bar_position,
    ) as pbar:
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
            tar.extractall(data_dir)
            pbar.update(total_size)


def install_datasets(force: bool = False):
    os.makedirs(data_dir, exist_ok=True)

    os.environ["GEANT4_DATA_DIR"] = data_dir
    datasets_to_download = []
    for dataset in datasets:
        path = os.path.join(data_dir, dataset.name + dataset.version)
        os.environ[dataset.env] = path
        if not os.path.exists(path) or force:
            datasets_to_download.append(dataset)

    if len(datasets_to_download) == 0:
        return

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(datasets_to_download)
    ) as executor:
        futures = [
            executor.submit(_download_extract_dataset, dataset, i)
            for i, dataset in enumerate(datasets_to_download)
        ]
        concurrent.futures.wait(futures)


def reinstall_datasets():
    install_datasets(force=True)
