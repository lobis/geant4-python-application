from __future__ import annotations

import multiprocessing
from collections import namedtuple

import geant4_python_application.datasets
from geant4_python_application._geant4_application import (
    Application as Geant4Application,
)

Message = namedtuple("Message", ["target", "method", "args", "kwargs"])


def _start_application(pipe: multiprocessing.Pipe):
    app = Geant4Application()

    while message := pipe.recv():
        if message is None:
            break
        target = message.target  # assume it's self for now
        method = message.method
        # verify that the method exists on app
        if not hasattr(app, method):
            raise ValueError(f"Unknown method: {method}")

        try:
            # call the method
            result = getattr(app, method)(*message.args, **message.kwargs)
            # send the result back
            pipe.send(result)
        except Exception as e:
            print(f"Exception in {method}: {e}")
            break


class Application:
    def __init__(self):
        geant4_python_application.datasets.install_datasets(show_progress=False)
        self.pipe, child_pipe = multiprocessing.Pipe()
        multiprocessing.Process(target=_start_application, args=(child_pipe,)).start()

    def __del__(self):
        try:
            self._send(None)
        except Exception:
            pass

    def _send(self, message: Message | None):
        self.pipe.send(message)

    def _recv(self):
        return self.pipe.recv()

    def _send_and_recv(self, message: Message):
        try:
            self._send(message)
            return self._recv()
        except Exception as e:
            raise RuntimeError(
                f"Application has been destroyed. Please create a new one: {e}"
            )

    def setup_manager(self, n_threads: int = 0) -> Application:
        self._send_and_recv(Message("self", "setup_manager", (n_threads,), {}))
        return self

    def setup_physics(self) -> Application:
        self._send_and_recv(Message("self", "setup_physics", (), {}))
        return self

    def setup_detector(self, gdml: str) -> Application:
        self._send_and_recv(Message("self", "setup_detector", (gdml,), {}))
        return self

    def setup_action(self) -> Application:
        self._send_and_recv(Message("self", "setup_action", (), {}))
        return self

    def initialize(self) -> Application:
        self._send_and_recv(Message("self", "initialize", (), {}))
        return self

    def run(self, n_events: int):
        return self._send_and_recv(Message("self", "run", (n_events,), {}))
