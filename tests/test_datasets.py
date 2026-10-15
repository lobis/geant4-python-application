from __future__ import annotations

import os

import geant4_python_application as g4
from geant4_python_application.files import datasets as ds


def test_reuse_datasets_from_other_geant4_version(tmp_path):
    previous = g4.application_directory()
    try:
        g4.application_directory(str(tmp_path))
        target = ds.application_data_directory()
        os.makedirs(target)
        other = os.path.join(os.path.dirname(os.path.dirname(target)), "0.0.0", "data")

        reusable, missing = ds.datasets[0], ds.datasets[1]
        source = os.path.join(other, reusable.name + reusable.version, "sub")
        os.makedirs(source)
        with open(os.path.join(source, "x.dat"), "w") as f:
            f.write("data")

        still_missing = ds._reuse_from_other_versions([reusable, missing])

        assert still_missing == [missing]
        copied = os.path.join(target, reusable.name + reusable.version, "sub", "x.dat")
        with open(copied) as f:
            assert f.read() == "data"
        assert os.stat(copied).st_ino == os.stat(os.path.join(source, "x.dat")).st_ino
        assert not any(name.endswith(".partial") for name in os.listdir(target))
    finally:
        g4.application_directory(previous)


def test_reuse_without_other_versions(tmp_path):
    previous = g4.application_directory()
    try:
        g4.application_directory(str(tmp_path))
        assert ds._reuse_from_other_versions(list(ds.datasets)) == list(ds.datasets)
    finally:
        g4.application_directory(previous)


def _fake_geant4_config(tmp_path, monkeypatch, version, with_all=True):
    data = tmp_path / "share" / "Geant4" / "data"
    lines = []
    for dataset in ds.datasets if with_all else ds.datasets[:-1]:
        # Geant4 11.4 installs e.g. G4NDL as NDL4.7.1, not G4NDL4.7.1
        name = dataset.name[2:] if dataset.name.startswith("G4") else dataset.name
        path = data / (name + dataset.version)
        path.mkdir(parents=True)
        lines.append(f"{dataset.name} INSTALLED {path}")
        monkeypatch.delenv(dataset.env, raising=False)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "geant4-config"
    listing = "\n".join(lines)
    script.write_text(
        "#!/bin/sh\n"
        f'case "$1" in --version) echo {version};; --check-datasets) cat <<"EOF2"\n{listing}\nEOF2\n;; esac\n'
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return data


def test_installation_datasets_from_geant4_config(tmp_path, monkeypatch):
    _fake_geant4_config(tmp_path, monkeypatch, g4.geant4_version)
    found = ds.installation_datasets()
    assert set(found) == {dataset.env for dataset in ds.datasets}
    assert found["G4NEUTRONHPDATA"].endswith("NDL4.7.1")


def test_installation_datasets_from_environment(tmp_path, monkeypatch):
    _fake_geant4_config(tmp_path, monkeypatch, g4.geant4_version, with_all=False)
    for dataset in ds.datasets:
        path = tmp_path / "env" / dataset.env
        path.mkdir(parents=True)
        monkeypatch.setenv(dataset.env, str(path))
    found = ds.installation_datasets()
    assert found == {dataset.env: str(tmp_path / "env" / dataset.env) for dataset in ds.datasets}


def test_installation_datasets_ignored_when_incomplete_or_other_version(
    tmp_path, monkeypatch
):
    _fake_geant4_config(tmp_path / "a", monkeypatch, "10.7.4")
    assert ds.installation_datasets() == {}
    _fake_geant4_config(tmp_path / "b", monkeypatch, g4.geant4_version, with_all=False)
    assert ds.installation_datasets() == {}
