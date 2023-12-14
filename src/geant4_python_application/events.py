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


ak.behavior["event"] = EventRecord
ak.behavior["*", "event"] = EventArray
