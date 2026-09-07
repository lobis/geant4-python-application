from __future__ import annotations

import multiprocessing
import threading
from collections import namedtuple

import awkward as ak

import geant4_python_application
import geant4_python_application.events
from geant4_python_application._geant4_application import (
    Application as Geant4Application,
)

Message = namedtuple("Message", ["target", "method", "args", "kwargs"])

_default_event_fields = {
    "run",
    "id",
    "primaries",
    "track_id",
    "track_parent_id",
    "track_initial_energy",
    "track_initial_time",
    "track_initial_position",
    "track_particle",
    "track_creator_process",
    "step_energy",
    "step_time",
    "step_process",
    "step_volume",
    "step_position",
}


def _start_application(pipe: multiprocessing.Pipe):
    app = Geant4Application()
    app.set_event_fields(_default_event_fields)
    while True:
        counter = None
        try:
            message_with_counter = pipe.recv()
            if message_with_counter is None:
                break

            counter, message = message_with_counter
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

            result = getattr(target, method)(*message.args, **message.kwargs)
            pipe.send((counter, result))
        except KeyboardInterrupt:
            pass
        except EOFError or BrokenPipeError:
            break
        except Exception as e:
            if counter is not None:
                pipe.send((counter, e))


class Application:
    def __init__(
        self,
        n_threads: int = 0,
        gdml: str = None,
        physics: str = "custom",
        optical: bool = False,
        seed: int = 0,
    ):
        geant4_python_application.install_datasets(show_progress=True)

        self._pipe, child_pipe = multiprocessing.Pipe()
        self._process = multiprocessing.Process(
            target=_start_application, args=(child_pipe,), daemon=True
        )
        self._message_counter = 0
        self._lock = threading.Lock()

        self._seed = seed
        self._detector = geant4_python_application.Detector(self)
        self._generator = geant4_python_application.Generator(self)
        self._n_threads = n_threads
        self._gdml = gdml
        self._physics = physics
        self._optical = optical

    def start(self, setup: bool = True, initialize: bool = False) -> Application:
        if self._process.is_alive():
            raise RuntimeError("Application is already running")
        self._process.start()

        if setup:
            self.seed = self._seed
            self.setup_manager(self._n_threads)
            self.setup_physics(self._physics, optical=self._optical)

            if self._gdml is not None:
                self.setup_detector(self._gdml)
                self.setup_action()

        if initialize:
            if not setup:
                raise ValueError("Cannot initialize without setup")
            self.initialize()

        return self

    def stop(self):
        if not self._process.is_alive():
            return
        try:
            self._pipe.send(None)
            self._pipe.close()
            self._process.join()
        except (EOFError, BrokenPipeError):
            pass

    def __enter__(self) -> Application:
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def _send(self, counter: int, message: Message):
        self._pipe.send((counter, message))

    def _recv(self):
        return self._pipe.recv()

    def _send_and_recv(self, message: Message):
        if self._process is None or not self._process.is_alive():
            raise RuntimeError("Application is not running")
        with self._lock:
            try:
                self._send(self._message_counter, message)
                counter, response = self._recv()
                if counter != self._message_counter:
                    raise RuntimeError("Message counter mismatch")
                self._message_counter += 1
            except (EOFError, BrokenPipeError):
                raise RuntimeError("Application process died. Recreate the application")
            if isinstance(response, Exception):
                raise response
            return response

    def setup_manager(self, n_threads: int = 0) -> Application:
        self._send_and_recv(Message("", "setup_manager", (n_threads,), {}))
        return self

    def setup_physics(
        self, physics_list: str = "custom", *, optical: bool = False
    ) -> Application:
        self._send_and_recv(
            Message("", "setup_physics", (physics_list, optical), {})
        )
        return self

    @staticmethod
    def available_physics_lists() -> list[str]:
        return list(Geant4Application.available_physics_lists())

    @staticmethod
    def available_extra_physics() -> list[str]:
        """Extra G4VPhysicsConstructor names usable with add_physics (incl. DNA)."""
        return list(Geant4Application.available_extra_physics())

    def add_physics(self, constructor_name: str) -> Application:
        """Register an extra physics constructor (e.g. DNA, optical, EM extra).

        Must be called after setup_physics and before initialize/run.
        Example: app.add_physics("G4EmDNAPhysics_option2")
        """
        self._send_and_recv(Message("", "add_physics", (constructor_name,), {}))
        return self

    def setup_detector(self, gdml: str) -> Application:
        self._send_and_recv(Message("", "setup_detector", (gdml,), {}))
        return self

    def setup_action(self) -> Application:
        self._send_and_recv(Message("", "setup_action", (), {}))
        return self

    def set_event_fields(self, fields: set[str]) -> Application:
        self._send_and_recv(Message("", "set_event_fields", (fields,), {}))
        return self

    def get_event_fields(self) -> set[str]:
        return self._send_and_recv(Message("", "get_event_fields", (), {}))

    def get_event_fields_complete(self) -> set[str]:
        return self._send_and_recv(Message("", "get_event_fields_complete", (), {}))

    def initialize(self) -> Application:
        self._send_and_recv(Message("", "initialize", (), {}))
        return self

    def run(self, primaries: int | ak.Array):
        # "run" returns a list of arrays, one for each thread
        events = self._send_and_recv(Message("", "run", (primaries,), {}))
        concatenated_dict = {
            key: ak.concatenate([d[key] for d in events], axis=0)
            for key in events[0].keys()
        }
        # make sure they all have the same length
        for key in concatenated_dict:
            if len(concatenated_dict[key]) != len(
                concatenated_dict[list(concatenated_dict.keys())[0]]
            ):
                raise ValueError(f"Length mismatch for key {key}")

        keys_to_remove = set()
        step_array_dict = {}
        for key in concatenated_dict:
            prefix = "step_"
            if key.startswith(prefix):
                new_key = key[len(prefix) :]
                step_array_dict[new_key] = concatenated_dict[key]
                keys_to_remove.add(key)

        track_array_dict = {}
        for key in concatenated_dict:
            prefix = "track_"
            if key.startswith(prefix):
                new_key = key[len(prefix) :]
                track_array_dict[new_key] = concatenated_dict[key]
                keys_to_remove.add(key)

        events = ak.Array(
            {
                **{
                    key: concatenated_dict[key]
                    for key in [
                        key for key in concatenated_dict if key not in keys_to_remove
                    ]
                },
                **(
                    {
                        "track": ak.Array(
                            {
                                **{
                                    key: track_array_dict[key]
                                    for key in track_array_dict
                                },
                                **(
                                    {
                                        "step": ak.Array(
                                            {
                                                **{
                                                    key: step_array_dict[key]
                                                    for key in step_array_dict
                                                }
                                            },
                                            with_name="step",
                                        )
                                    }
                                    if len(step_array_dict) > 0
                                    else {}
                                ),
                            },
                            with_name="track",
                        )
                    }
                    if len(track_array_dict) > 0 or len(step_array_dict) > 0
                    else {}
                ),
            },
            with_name="event",
        )

        # events = ak.str.to_categorical(events)
        if "id" in events.fields:
            events = events[ak.argsort(events.id)]
        return events

    def run_with_callbacks(
        self,
        primaries: int | ak.Array,
        *,
        on_run=None,
        on_event=None,
        on_track=None,
        on_step=None,
    ):
        """Run then invoke Python callbacks over run/event/track/step records.

        Offline (post-run) layer over the awkward event model:
        on_run(events), on_event(event) per event, on_track(track, event)
        per track, on_step(step, track, event) per step. Returns events.

        Note: events.track is a struct-of-lists per event (see DataModel),
        so tracks/steps are reconstructed via ak.zip per event/track.
        """
        events = self.run(primaries)
        if on_run is not None:
            on_run(events)
        if on_event is None and on_track is None and on_step is None:
            return events
        for ei in range(len(events)):
            event = events[ei]
            if on_event is not None:
                on_event(event)
            if on_track is None and on_step is None:
                continue
            if "track" not in event.fields:
                continue
            track_struct = event.track
            if "id" not in track_struct.fields:
                continue
            n_tracks = len(track_struct.id)
            track_only_fields = [f for f in track_struct.fields if f != "step"]
            has_steps = "step" in track_struct.fields
            for ti in range(n_tracks):
                # Lightweight dict view (scalars/vectors); steps as awkward array.
                track_view = {f: track_struct[f][ti] for f in track_only_fields}
                steps_view = None
                if has_steps:
                    step_struct = track_struct.step
                    steps_view = ak.zip(
                        {f: step_struct[f][ti] for f in step_struct.fields}
                    )
                    track_view = dict(track_view)
                    track_view["step"] = steps_view
                if on_track is not None:
                    on_track(track_view, event)
                if on_step is None or steps_view is None:
                    continue
                for step in steps_view:
                    on_step(step, track_view, event)
        return events

    @property
    def seed(self):
        return self._send_and_recv(Message("", "get_seed", (), {}))

    @seed.setter
    def seed(self, seed: int):
        self._send_and_recv(Message("", "set_seed", (seed,), {}))

    def command(self, command: str) -> Application:
        self._send_and_recv(Message("", "command", (command,), {}))
        return self

    def commands(self, commands: list[str]) -> Application:
        for command in commands:
            self.command(command)
        return self

    def list_commands(self, directory="/") -> str:
        return self._send_and_recv(Message("", "list_commands", (directory,), {}))

    @staticmethod
    def visualization_available() -> bool:
        return Geant4Application.visualization_available()

    @staticmethod
    def multithreading_available() -> bool:
        """Whether the linked Geant4 runtime supports multithreaded run managers."""
        return Geant4Application.multithreading_available()

    def visualize(self, commands: list[str] | None = None) -> Application:
        """Open the interactive Geant4 Qt viewer.

        The call returns after the viewer is closed. Geant4 commands can be
        entered in the Qt session's command panel while it is open.
        """
        if commands is None:
            commands = [
                "/vis/open OGL",
                "/vis/drawVolume",
                "/vis/viewer/set/autoRefresh true",
                "/vis/scene/add/trajectories smooth",
                "/vis/scene/endOfEventAction accumulate",
            ]
        self._send_and_recv(Message("", "visualize", (commands,), {}))
        return self

    @property
    def detector(self) -> geant4_python_application.Detector:
        return self._detector

    @property
    def generator(self) -> geant4_python_application.Generator:
        return self._generator
