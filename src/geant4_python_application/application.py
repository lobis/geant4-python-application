from __future__ import annotations

import multiprocessing
from collections import namedtuple

from geant4_python_application.geant4_application import Application

Message = namedtuple("Message", ["target", "method", "args", "kwargs"])


def _start_application(pipe: multiprocessing.Pipe):
    app = Application()

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


class App:
    def __init__(self):
        self.pipe, child_pipe = multiprocessing.Pipe()
        multiprocessing.Process(target=_start_application, args=(child_pipe,)).start()

    def __del__(self):
        self._send(None)

    def _send(self, message: Message | None):
        # check for broken pipe
        try:
            self.pipe.send(message)
        except Exception as e:
            raise RuntimeError(
                f"Application has been destroyed. Please create a new one: {e}"
            )

    def _recv(self):
        try:
            return self.pipe.recv()
        except Exception as e:
            raise RuntimeError(
                f"Application has been destroyed. Please create a new one: {e}"
            )

    def setup_manager(self):
        self._send(Message("self", "setup_manager", (), {}))
        self._recv()

    def setup_physics(self):
        self._send(Message("self", "setup_physics", (), {}))
        self._recv()

    def setup_detector(self, gdml: str):
        self._send(Message("self", "setup_detector", (gdml,), {}))
        self._recv()

    def setup_action(self):
        self._send(Message("self", "setup_action", (), {}))
        self._recv()

    def initialize(self):
        self._send(Message("self", "initialize", (), {}))
        self._recv()

    def run(self, n_events: int):
        self._send(Message("self", "run", (n_events,), {}))
        return self._recv()
