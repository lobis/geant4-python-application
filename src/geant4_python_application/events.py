from __future__ import annotations

import awkward as ak
import numpy as np


class EventRecord(ak.Record):
    def energy_in_volume(self, volume: str) -> float:
        energy = self.track.step.energy[self.track.step.volume == volume]
        # collapse to a scalar
        return ak.sum(energy)


class EventArray(ak.Array):
    def energy_in_volume(self, volume: str) -> ak.Array:
        energy = self.track.step.energy[self.track.step.volume == volume]
        # collapse to an array of scalars (one per event)
        return ak.sum(ak.flatten(energy, axis=-1), axis=1)

    def hits(self, volume: str | None = None) -> ak.Array:
        hits = ak.flatten(self.track.step, axis=-1)
        hits = hits[hits.energy > 0]
        if volume is not None:
            hits = hits[hits.volume == volume]
        # only keep x,y,z, time, and energy
        hits = hits[["position_x", "position_y", "position_z", "time", "energy"]]
        return ak.Array(hits, with_name="hits")


class HitsRecord(ak.Record):
    # This is really expensive!
    def electrons(self, work_function: float = 20.0 / 1e3) -> ak.Array:
        n_electrons = np.round(self.energy / work_function)
        return ak.flatten(
            ak.Array(
                [
                    [
                        {
                            "position_x": self.position_x[i],
                            "position_y": self.position_y[i],
                            "position_z": self.position_z[i],
                            "time": self.time[i],
                        }
                        for _ in range(int(n_electrons[i]))
                    ]
                    for i in range(len(self.energy))
                ],
                with_name="electrons",
            )
        )


ak.behavior["event"] = EventRecord
ak.behavior["*", "event"] = EventArray

ak.behavior["hits"] = HitsRecord
