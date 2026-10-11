from __future__ import annotations

"""MPI / distributed helpers with graceful fallback (no hard mpi4py dep)."""

import os


def get_rank_size() -> tuple[int, int]:
    """Return (rank, size) from mpi4py if available, else env vars, else (0,1)."""
    try:
        from mpi4py import MPI  # type: ignore

        comm = MPI.COMM_WORLD
        return int(comm.Get_rank()), int(comm.Get_size())
    except Exception:
        pass
    for rank_var, size_var in [
        ("OMPI_COMM_WORLD_RANK", "OMPI_COMM_WORLD_SIZE"),
        ("PMI_RANK", "PMI_SIZE"),
        ("MPI_RANK", "MPI_SIZE"),
    ]:
        if rank_var in os.environ and size_var in os.environ:
            try:
                return int(os.environ[rank_var]), int(os.environ[size_var])
            except ValueError:
                continue
    return 0, 1


def split_count(n_total: int, rank: int, size: int) -> tuple[int, int]:
    """Return (start, count) for rank under even split of n_total events."""
    if n_total < 0 or rank < 0 or size <= 0 or rank >= size:
        msg = f"invalid split args: n={n_total} rank={rank} size={size}"
        raise ValueError(msg)
    base, rem = divmod(n_total, size)
    start = rank * base + min(rank, rem)
    count = base + (1 if rank < rem else 0)
    return start, count


def local_count(n_total: int) -> tuple[int, int, int]:
    """Return (rank, size, count) for this process."""
    rank, size = get_rank_size()
    _, count = split_count(n_total, rank, size)
    return rank, size, count
