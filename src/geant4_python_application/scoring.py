from __future__ import annotations

import awkward as ak
import numpy as np


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
