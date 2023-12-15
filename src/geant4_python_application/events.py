from __future__ import annotations

import awkward as ak


class EventRecord(ak.Record):
    def energy_in_volume(self, volume) -> float:
        energy = self.track.step.energy[self.track.step.volume == volume]
        # collapse to a scalar
        return ak.sum(energy)


class EventArray(ak.Array):
    def energy_in_volume(self, volume) -> ak.Array:
        energy = self.track.step.energy[self.track.step.volume == volume]
        # collapse to an array of scalars (one per event)
        return ak.flatten(ak.sum(energy, axis=-1))

    def hits(self, volume) -> ak.Array:
        hits = ak.flatten(self.track.step, axis=-1)
        hits = hits[hits.volume == volume][hits.energy > 0]
        # only keep x,y,z, time, and energy
        hits = hits[["position_x", "position_y", "position_z", "time", "energy"]]
        return hits


ak.behavior["event"] = EventRecord
ak.behavior["*", "event"] = EventArray
