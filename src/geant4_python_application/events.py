from __future__ import annotations

import awkward as ak
import numpy as np
import vector


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
        hits = hits[["position", "time", "energy"]]
        return ak.Array(hits, with_name="geant4_hits")


class HitsRecord(ak.Record):
    # This is really expensive!
    def electrons(self, work_function: float = 20.0 / 1e3) -> ak.Array:
        n_electrons = np.round(self.energy / work_function)
        return ak.flatten(
            ak.Array(
                [
                    [
                        {
                            "position": self.position[i],
                            "time": self.time[i],
                        }
                        for _ in range(int(n_electrons[i]))
                    ]
                    for i in range(len(self.energy))
                ],
                with_name="geant4_tpc_electrons",
            )
        )


class ElectronsRecord(ak.Array):
    def drift(
        self,
        *,
        drift_velocity: float,
        longitudinal_diffusion: float,
        transversal_diffusion: float,
        plane_point: tuple[float, float, float],
        plane_normal: tuple[float, float, float],
    ) -> ElectronsRecord:
        # TODO: not working yet
        plane_normal = vector.obj(
            x=plane_normal[0], y=plane_normal[1], z=plane_normal[2]
        ).unit()
        assert np.isclose(plane_normal.mag, 1.0)
        plane_point = vector.obj(x=plane_point[0], y=plane_point[1], z=plane_point[2])
        distance_to_plane = (self.position - plane_point) * plane_normal
        self.time += distance_to_plane / drift_velocity + np.random.normal(
            0, longitudinal_diffusion * distance_to_plane, len(self.time)
        )
        self.position += -distance_to_plane * plane_normal
        self.position += np.random.normal(
            0, transversal_diffusion * distance_to_plane, len(self.position)
        )
        return self


ak.behavior["geant4_event"] = EventRecord
ak.behavior["*", "geant4_event"] = EventArray

ak.behavior["geant4_hits"] = HitsRecord

ak.behavior["geant4_tpc_electrons"] = ElectronsRecord
