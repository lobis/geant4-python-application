"""Wall-time breakdown of geant4_python_application runs, to judge GPU offload.

Question: would offloading e-/e+/gamma transport to a GPU (Celeritas/AdePT)
or optical photons to Opticks speed this package up, or is the time spent
recording steps into awkward builders and handing the result to Python?

Every workload/thread-count pair is measured in two fresh processes:

1. In-process: the compiled ``_geant4_application.Application`` (what the
   public ``Application`` drives in its child process), timing ``run()``.
   That is BeamOn plus the builder -> awkward snapshot in EndOfRunAction,
   with no pipe.  Event-field variants:

   * ``minimal``    -- fields {"id"}: Geant4 transport with step recording
     reduced as far as the API allows.  SteppingAction still calls
     data::InsertStep for every step; with no step field selected it only
     does ~10 hash-set lookups and copies the process name.
   * ``default``    -- the package's default event fields.
   * ``no-optical`` -- optical workload only: minimal with Scintillation
     and Cerenkov inactivated, so minimal - no-optical is the cost of
     generating and tracking optical photons.

2. Public API: ``geant4_python_application.Application.run`` with the
   default fields, timed in this process, with the time spent waiting for
   the child process (``_send_and_recv``) recorded separately.

Then, for the default fields,

    transport  = in-process minimal
    recording  = in-process default - in-process minimal - snapshot estimate
    snapshot   = ak.to_buffers + ak.from_buffers over the returned arrays
                 (a proxy for the C++ to_buffers + from_buffers in
                 EndOfRunAction, which cannot be timed from outside)
    ipc        = public child wait - in-process default  (moving the
                 awkward arrays to the parent: one shared-memory block for
                 results over 1 MB, else pickle + multiprocessing.Pipe; see
                 geant4_python_application._transfer)
    python     = public total - public child wait  (concatenate, build the
                 Geant4Event record, sort by id)

Usage::

    python tools/profile_breakdown.py --threads 0 8 --out tmp/profile.json

``--threads 0`` is the serial run manager.  Prints one markdown table per
workload; ``--out`` also saves the raw numbers as JSON.  Multithreaded runs
use events-per-thread times the thread count.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import re
import statistics
import sys
import time
from pathlib import Path

import awkward as ak

import geant4_python_application as g4
from geant4_python_application import _transfer
from geant4_python_application.application import Message, _default_event_fields

# ~20 X0 of PbWO4 (X0 = 0.89 cm) along z, 30 cm x 30 cm transverse
# (Moliere radius 2.0 cm), in vacuum.
PBWO4_GDML = R"""<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
    <solids>
        <box name="WorldSolid" x="600" y="600" z="600" lunit="mm"/>
        <box name="CaloSolid" x="300" y="300" z="178" lunit="mm"/>
    </solids>
    <structure>
        <volume name="CaloVolume">
            <materialref ref="G4_PbWO4"/>
            <solidref ref="CaloSolid"/>
        </volume>
        <volume name="World">
            <materialref ref="G4_Galactic"/>
            <solidref ref="WorldSolid"/>
            <physvol name="calo">
                <volumeref ref="CaloVolume"/>
                <position name="caloPosition" unit="mm" x="0" y="0" z="89"/>
            </physvol>
        </volume>
    </structure>
    <setup name="Default" version="1.0"><world ref="World"/></setup>
</gdml>
"""

# 1 m water cube; a 10 MeV gamma has a ~50 cm mean free path in water.
WATER_GDML = R"""<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
    <solids>
        <box name="WorldSolid" x="1200" y="1200" z="1200" lunit="mm"/>
        <box name="WaterSolid" x="1000" y="1000" z="1000" lunit="mm"/>
    </solids>
    <structure>
        <volume name="WaterVolume">
            <materialref ref="G4_WATER"/>
            <solidref ref="WaterSolid"/>
        </volume>
        <volume name="World">
            <materialref ref="G4_AIR"/>
            <solidref ref="WorldSolid"/>
            <physvol name="water">
                <volumeref ref="WaterVolume"/>
                <position name="waterPosition" unit="mm" x="0" y="0" z="0"/>
            </physvol>
        </volume>
    </structure>
    <setup name="Default" version="1.0"><world ref="World"/></setup>
</gdml>
"""

WORKLOADS = {
    "em_calo": {
        "title": "1 GeV e- into 20 X0 PbWO4",
        "gdml": PBWO4_GDML,
        "optical": False,
        "commands": [
            "/gun/particle e-",
            "/gun/energy 1 GeV",
            "/gun/position 0 0 -10 mm",
            "/gun/direction 0 0 1",
        ],
        "events": 10,
    },
    "gamma_water": {
        "title": "10 MeV gamma into water",
        "gdml": WATER_GDML,
        "optical": False,
        "commands": [
            "/gun/particle gamma",
            "/gun/energy 10 MeV",
            "/gun/position 0 0 -499 mm",
            "/gun/direction 0 0 1",
        ],
        "events": 2000,
    },
    "optical": {
        "title": "10 MeV e- in optical water scintillator (optical.optical_water_gdml)",
        "gdml": g4.optical.optical_water_gdml,
        "optical": True,
        # As in examples/geant4-examples/05_optical_scintillation.py
        "commands": g4.optical.scintillation_commands(
            stack_photons=True, max_cerenkov=100
        )
        + [
            "/gun/particle e-",
            "/gun/energy 10 MeV",
            "/gun/position 0 0 0 mm",
            "/gun/direction 1 0 0",
        ],
        "events": 50,
    },
}

MINIMAL_FIELDS = {"id"}
DEFAULT_FIELDS = set(_default_event_fields)
OPTICAL_PROCESSES = ("Scintillation", "Cerenkov")

CATEGORIES = ["e-", "e+", "gamma", "opticalphoton", "hadrons", "other"]
_ION = re.compile(r"^[A-Z][a-z]?\d+(\[.*\])?$")
HADRONS = {
    "proton",
    "neutron",
    "pi+",
    "pi-",
    "pi0",
    "kaon+",
    "kaon-",
    "kaon0L",
    "kaon0S",
}


def categorize(name: str) -> str:
    if name in ("e-", "e+", "gamma", "opticalphoton"):
        return name
    if (
        name in HADRONS
        or name in ("deuteron", "triton", "alpha", "He3")
        or _ION.match(name)
    ):
        # nuclear recoils and fragments ("O16", "Pb207[569.7]") count as hadrons
        return "hadrons"
    return "other"


def count_particles(events) -> dict:
    names = ak.to_list(ak.flatten(events.track.particle, axis=None))
    steps = ak.to_numpy(ak.flatten(ak.num(events.track.step.energy, axis=2), axis=None))
    tracks_by = dict.fromkeys(CATEGORIES, 0)
    steps_by = dict.fromkeys(CATEGORIES, 0)
    for name, n in zip(names, steps):
        cat = categorize(name)
        tracks_by[cat] += 1
        steps_by[cat] += int(n)
    return {"tracks": tracks_by, "steps": steps_by, "events": len(events)}


def snapshot_estimate(raw) -> float:
    """Seconds to flatten and rebuild every per-thread array (EndOfRunAction proxy)."""
    t0 = time.perf_counter()
    for per_thread in raw:
        for array in per_thread.values():
            form, length, buffers = ak.to_buffers(array)
            ak.from_buffers(form, length, buffers)
    return time.perf_counter() - t0


def median_and_samples(samples: list[float]) -> dict:
    return {"median": statistics.median(samples), "samples": samples}


# -- 1. in-process ------------------------------------------------------------


def _inprocess(
    workload: str, n_threads: int, n_events: int, repeats: int, seed: int, queue
) -> None:
    try:
        from geant4_python_application._geant4_application import Application

        g4.install_datasets(show_progress=False)
        spec = WORKLOADS[workload]
        app = Application()
        app.set_seed(seed)
        app.setup_manager(n_threads)
        app.setup_physics("custom", spec["optical"])
        app.setup_detector(spec["gdml"])
        app.setup_action()
        for command in spec["commands"]:
            app.command(command)
        app.initialize()

        warm = min(n_events, 2 * max(n_threads, 1))

        def timed(fields: set[str]) -> list[float]:
            app.set_event_fields(fields)
            app.run(warm)
            out = []
            for _ in range(repeats):
                t0 = time.perf_counter()
                app.run(n_events)
                out.append(time.perf_counter() - t0)
            return out

        result = {"minimal": timed(MINIMAL_FIELDS), "default": timed(DEFAULT_FIELDS)}
        if spec["optical"]:
            # (In)activating a process marks the physics modified, so the next
            # BeamOn rebuilds tables on every thread; timed() warms up first.
            for process in OPTICAL_PROCESSES:
                app.command(f"/process/deactivate {process}")
            result["no-optical"] = timed(MINIMAL_FIELDS)
            app.set_event_fields({"id", "track_particle"})
            check = app.run(warm)
            result["no_optical_photons_seen"] = int(
                sum(ak.sum(d["track_particle"] == "opticalphoton") for d in check)
            )
        queue.put(result)
    except BaseException as error:  # report instead of hanging the parent
        queue.put({"error": repr(error)})
        raise


def run_inprocess(
    workload: str, n_threads: int, n_events: int, repeats: int, seed: int
) -> dict:
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(
        target=_inprocess, args=(workload, n_threads, n_events, repeats, seed, queue)
    )
    process.start()
    result = queue.get()
    process.join()
    if "error" in result:
        raise RuntimeError(f"in-process run failed: {result['error']}")
    return {
        key: median_and_samples(value) if isinstance(value, list) else value
        for key, value in result.items()
    }


# -- 2. public API ------------------------------------------------------------


class TimedApplication(g4.Application):
    """Records how long Application.run waits for the Geant4 child process."""

    last_child_seconds: float = 0.0
    last_raw = None

    def _send_and_recv(self, message: Message):
        if message.method != "run":
            return super()._send_and_recv(message)
        t0 = time.perf_counter()
        result = super()._send_and_recv(message)
        self.last_child_seconds = time.perf_counter() - t0
        self.last_raw = result
        return result


def run_public(
    workload: str, n_threads: int, n_events: int, repeats: int, seed: int
) -> dict:
    spec = WORKLOADS[workload]
    app = TimedApplication(
        n_threads=n_threads, gdml=spec["gdml"], optical=spec["optical"], seed=seed
    )
    totals, child_seconds, snapshots, sizes = [], [], [], []
    counts = None
    stats_before = dict(_transfer.stats)
    with app:
        app.commands(spec["commands"])
        app.initialize()
        app.set_event_fields({"id"})
        app.run(min(n_events, 2 * max(n_threads, 1)))
        app.set_event_fields(DEFAULT_FIELDS)
        for _ in range(repeats):
            t0 = time.perf_counter()
            events = app.run(n_events)
            totals.append(time.perf_counter() - t0)
            child_seconds.append(app.last_child_seconds)
            snapshots.append(snapshot_estimate(app.last_raw))
            sizes.append(sum(a.layout.nbytes for d in app.last_raw for a in d.values()))
            app.last_raw = None
            if counts is None:
                counts = count_particles(events)
            del events
    return {
        "transfer": {k: _transfer.stats[k] - stats_before[k] for k in stats_before},
        "total": median_and_samples(totals),
        "child": median_and_samples(child_seconds),
        "snapshot_est": median_and_samples(snapshots),
        "bytes": statistics.median(sizes),
        "counts": counts,
    }


# -- report -------------------------------------------------------------------


def breakdown(res: dict) -> dict:
    inproc, public = res["inprocess"], res["public"]
    minimal = inproc["minimal"]["median"]
    default = inproc["default"]["median"]
    snapshot = public["snapshot_est"]["median"]
    total = public["total"]["median"]
    child = public["child"]["median"]
    out = {
        "total": total,
        "transport": minimal,
        "recording": default - minimal - snapshot,
        "snapshot": snapshot,
        "ipc": child - default,
        "python": total - child,
    }
    if "no-optical" in inproc:
        out["optical_photons"] = minimal - inproc["no-optical"]["median"]
    return out


def pct(x: float, total: float) -> str:
    return f"{x:.2f} ({100 * x / total:.0f}%)"


def markdown(all_results: list[dict]) -> str:
    lines = []
    by_workload: dict = {}
    for r in all_results:
        by_workload.setdefault(r["workload"], []).append(r)
    for workload, results in by_workload.items():
        lines.append(f"### {WORKLOADS[workload]['title']}\n")
        bds = [breakdown(r) for r in results]
        header = [
            "seconds (share of public-API wall)",
            *[f"{r['threads']} thr, {r['events']} ev" for r in results],
        ]
        rows = [
            [
                "**wall, `Application.run`, default fields**",
                *[f"**{b['total']:.2f}**" for b in bds],
            ],
            [
                "G4 transport (fields {id})",
                *[pct(b["transport"], b["total"]) for b in bds],
            ],
        ]
        if "optical_photons" in bds[0]:
            rows.append(
                [
                    "  of which optical photons",
                    *[pct(b["optical_photons"], b["total"]) for b in bds],
                ]
            )
        rows += [
            [
                "step/track recording (InsertStep etc.)",
                *[pct(b["recording"], b["total"]) for b in bds],
            ],
            [
                "builder -> awkward snapshot (est.)",
                *[pct(b["snapshot"], b["total"]) for b in bds],
            ],
            [
                "result transfer to parent process",
                *[pct(b["ipc"], b["total"]) for b in bds],
            ],
            [
                "  runs via shm / pipe (incl. warm-up)",
                *[
                    "{} / {}".format(
                        *(
                            r["public"].get("transfer", {}).get(k, "?")
                            for k in ("shared_memory", "pipe")
                        )
                    )
                    for r in results
                ],
            ],
            [
                "Python assembly in Application.run",
                *[pct(b["python"], b["total"]) for b in bds],
            ],
            [
                "in-process wall, fields {id} / default",
                *[
                    f"{r['inprocess']['minimal']['median']:.2f} / {r['inprocess']['default']['median']:.2f}"
                    for r in results
                ],
            ],
            [
                "events/s: public API / in-process {id}",
                *[
                    f"{r['events'] / b['total']:.0f} / {r['events'] / b['transport']:.0f}"
                    for r, b in zip(results, bds)
                ],
            ],
            [
                "output size (MB, awkward buffers)",
                *[f"{r['public']['bytes'] / 1e6:.0f}" for r in results],
            ],
        ]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
        lines += ["| " + " | ".join(row) + " |" for row in rows]
        lines.append("")

        c = results[0]["public"]["counts"]
        total_steps = sum(c["steps"].values()) or 1
        total_tracks = sum(c["tracks"].values()) or 1
        lines.append(f"Tracks and steps by particle ({c['events']} events):\n")
        lines.append("| particle | tracks/event | steps/event | step share |")
        lines.append("|---|---|---|---|")
        for cat in CATEGORIES:
            t, s = c["tracks"][cat], c["steps"][cat]
            if t or s:
                lines.append(
                    f"| {cat} | {t / c['events']:.1f} | {s / c['events']:.1f} | {100 * s / total_steps:.1f}% |"
                )
        em = sum(c["steps"][k] for k in ("e-", "e+", "gamma"))
        lines.append(
            f"| **all** | {total_tracks / c['events']:.1f} | {total_steps / c['events']:.1f} | "
            f"e±/γ {100 * em / total_steps:.1f}%, optical {100 * c['steps']['opticalphoton'] / total_steps:.1f}% |"
        )
        seen = results[0]["inprocess"].get("no_optical_photons_seen")
        if seen is not None:
            lines.append(
                f"\n(no-optical check: {seen} optical photons with Scintillation and Cerenkov inactivated)"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--workloads", nargs="+", default=list(WORKLOADS), choices=list(WORKLOADS)
    )
    parser.add_argument(
        "--threads", nargs="+", type=int, default=[0, 8], help="0 = serial run manager"
    )
    parser.add_argument(
        "--events", type=float, default=1.0, help="scale the per-workload event counts"
    )
    parser.add_argument(
        "--no-scale",
        action="store_true",
        help="do not multiply events by the thread count",
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument(
        "--out", type=Path, default=None, help="write raw results as JSON"
    )
    args = parser.parse_args(argv)

    print(
        f"geant4_python_application {g4.__version__}, Geant4 {g4.geant4_version}, awkward {ak.__version__}",
        file=sys.stderr,
    )
    all_results = []
    for workload in args.workloads:
        for n_threads in args.threads:
            n = int(round(WORKLOADS[workload]["events"] * args.events))
            if not args.no_scale and n_threads > 1:
                n *= n_threads
            print(
                f"[{workload}] threads={n_threads} events={n} ...",
                file=sys.stderr,
                flush=True,
            )
            t0 = time.perf_counter()
            res = {
                "workload": workload,
                "threads": max(n_threads, 1),
                "events": n,
                "inprocess": run_inprocess(
                    workload, n_threads, n, args.repeats, args.seed
                ),
                "public": run_public(workload, n_threads, n, args.repeats, args.seed),
            }
            print(
                f"  done in {time.perf_counter() - t0:.1f}s: {json.dumps(breakdown(res))}",
                file=sys.stderr,
                flush=True,
            )
            all_results.append(res)
            if args.out is not None:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(json.dumps(all_results, indent=1))
    print(markdown(all_results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
