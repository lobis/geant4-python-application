from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import awkward as ak
import numpy as np

if TYPE_CHECKING:
    from geant4_python_application.application import Application


class NativeScoringMesh:
    """Configure a Geant4 command-based Cartesian scoring mesh.

    This uses Geant4's native ``G4ScoringManager`` commands. It is distinct
    from :class:`Scoring`, which bins recorded steps in Python after a run.
    """

    def __init__(
        self,
        application: Application,
        name: str = "mesh",
        quantity: str = "eDep",
    ):
        self.application = application
        self.name = name
        self.quantity = quantity
        self._closed = False

    def box(
        self,
        half_size: tuple[float, float, float],
        bins: tuple[int, int, int],
        *,
        unit: str = "mm",
        center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> NativeScoringMesh:
        """Create a box mesh; ``half_size`` follows Geant4 mesh semantics."""
        if self._closed:
            raise RuntimeError("scoring mesh is already closed")
        sx, sy, sz = half_size
        nx, ny, nz = bins
        cx, cy, cz = center
        self.application.commands(
            [
                f"/score/create/boxMesh {self.name}",
                f"/score/mesh/boxSize {sx} {sy} {sz} {unit}",
                f"/score/mesh/nBin {nx} {ny} {nz}",
                f"/score/mesh/translate/xyz {cx} {cy} {cz} {unit}",
                f"/score/quantity/energyDeposit {self.quantity}",
                "/score/close",
            ]
        )
        self._closed = True
        return self

    def dump(self, path: str | Path, *, option: str = "") -> Path:
        """Dump the native mesh quantity after a run and return its path."""
        if not self._closed:
            raise RuntimeError("configure and close the scoring mesh before dumping")
        output = Path(path).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        if " " in str(output):
            raise ValueError("Geant4 scoring output paths cannot contain spaces")
        suffix = f" {option}" if option else ""
        self.application.command(
            f"/score/dumpQuantityToFile {self.name} {self.quantity} {output}{suffix}"
        )
        return output


class Scoring:
    """Scoring operations over Geant4 event, track, and step records."""

    @staticmethod
    def energy_deposit(events: ak.Array, volume: str | None = None) -> ak.Array:
        """Return deposited energy in keV for each event."""
        steps = events.track.step
        energy = steps.energy
        if volume is not None:
            energy = energy[steps.volume == volume]
        return ak.sum(ak.flatten(energy, axis=-1), axis=1)

    @staticmethod
    def hits(events: ak.Array, volume: str | None = None) -> ak.Array:
        """Return positive-energy steps, optionally restricted to a volume."""
        return events.hits(volume)

    @staticmethod
    def energy_mesh(
        events: ak.Array,
        bins: int | tuple[int, int, int] = 10,
        mesh_range: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
        | None = None,
        volume: str | None = None,
    ) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Bin step energy into a Cartesian 3D mesh.

        Positions are in millimetres and mesh values are deposited energy in keV.
        """
        hits = Scoring.hits(events, volume)
        weights = ak.to_numpy(ak.flatten(hits.energy, axis=None))
        if len(weights) == 0:
            shape = (bins, bins, bins) if isinstance(bins, int) else bins
            return np.zeros(shape), (np.array([]), np.array([]), np.array([]))

        points = np.column_stack(
            [
                ak.to_numpy(ak.flatten(hits.position.x, axis=None)),
                ak.to_numpy(ak.flatten(hits.position.y, axis=None)),
                ak.to_numpy(ak.flatten(hits.position.z, axis=None)),
            ]
        )
        mesh, edges = np.histogramdd(
            points, bins=bins, range=mesh_range, weights=weights
        )
        return mesh, edges
