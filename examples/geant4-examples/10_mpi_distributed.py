"""10 - MPI and distributed execution.

Shows rank/size detection (mpi4py -> env vars -> serial fallback) and
even event splitting. Each rank runs its share; gather with
awkward.concatenate or ROOT/parquet.
Run serial: python 10_mpi_distributed.py
Run MPI: mpiexec -n 2 python 10_mpi_distributed.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import geant4_python_application as g4
    from geant4_python_application import distributed as dist

    rank, size = dist.get_rank_size()
    print(f"rank {rank}/{size}")

    n_total = 4
    start, count = dist.split_count(n_total, rank, size)
    print(f"this rank handles events [{start}:{start + count}] of {n_total}")

    # Each rank runs only its share (here 2 events max per rank for speed)
    n_local = min(count, 2) if count else 0
    if n_local:
        with g4.Application(gdml=g4.basic_gdml, seed=100 + rank) as app:
            app.command("/gun/particle gamma")
            app.command("/gun/energy 1 MeV")
            events = app.run(n_local)
            print(f"rank {rank} ran {len(events)} event(s), ids: {list(events.id)}")
    else:
        print(f"rank {rank} has no work")

    # Pure splitting logic checks (run on every rank)
    assert dist.split_count(10, 0, 2) == (0, 5)
    assert dist.split_count(10, 1, 2) == (5, 5)
    print("split logic OK")

    if "--vis" in sys.argv and rank == 0:
        with g4.Application(gdml=g4.basic_gdml, seed=100) as app:
            app.command("/gun/particle gamma")
            app.command("/gun/energy 1 MeV")
            app.visualize()  # Qt viewer (rank 0 only); close window to return


if __name__ == "__main__":
    main()
