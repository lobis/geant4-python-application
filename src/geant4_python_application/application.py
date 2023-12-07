from __future__ import annotations

import multiprocessing
from collections import namedtuple

import geant4_python_application
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
        target = app
        target_list = message.target.split(".")
        target_list = [element for element in target_list if element]
        for target_name in target_list:
            if not hasattr(target, target_name):
                raise ValueError(f"{target} has no attribute {target_name}")
            target = getattr(target, target_name)

        method = message.method
        # verify that the method exists on app
        if not hasattr(target, method):
            raise ValueError(f"Unknown method: {method}")

        try:
            # call the method
            result = getattr(target, method)(*message.args, **message.kwargs)
            # send the result back
            pipe.send(result)
        except Exception as e:
            print(f"Exception in {method}: {e}")
            break


class Application:
    def __init__(self):
        geant4_python_application.datasets.install_datasets(show_progress=False)
        self._detector = geant4_python_application.Detector(self)

        self._pipe, child_pipe = multiprocessing.Pipe()
        self._process = multiprocessing.Process(
            target=_start_application, args=(child_pipe,), daemon=True
        )
        self._process.start()

    def __del__(self):
        try:
            self._send(None)
        except Exception:
            pass

    def _send(self, message: Message | None):
        self._pipe.send(message)

    def _recv(self):
        return self._pipe.recv()

    def _send_and_recv(self, message: Message):
        try:
            self._send(message)
            return self._recv()
        except Exception as e:
            raise RuntimeError(
                f"Application has been destroyed. Please create a new one: {e}"
            )

    def setup_manager(self, n_threads: int = 0) -> Application:
        self._send_and_recv(Message("", "setup_manager", (n_threads,), {}))
        return self

    def setup_physics(self) -> Application:
        self._send_and_recv(Message("", "setup_physics", (), {}))
        return self

    def setup_detector(self, gdml: str) -> Application:
        self._send_and_recv(Message("", "setup_detector", (gdml,), {}))
        return self

    def setup_action(self) -> Application:
        self._send_and_recv(Message("", "setup_action", (), {}))
        return self

    def initialize(self) -> Application:
        self._send_and_recv(Message("", "initialize", (), {}))
        return self

    def run(self, n_events: int):
        return self._send_and_recv(Message("", "run", (n_events,), {}))

    @property
    def seed(self):
        return self._send_and_recv(Message("", "get_seed", (), {}))

    @seed.setter
    def seed(self, seed: int):
        self._send_and_recv(Message("", "set_seed", (seed,), {}))

    def command(self, command: str) -> str:
        return self._send_and_recv(Message("", "command", (command,), {}))

    def list_commands(self, directory="/") -> str:
        return self._send_and_recv(Message("", "list_commands", (directory,), {}))

    @property
    def detector(self) -> geant4_python_application.Detector:
        return self._detector
