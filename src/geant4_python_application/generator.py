from __future__ import annotations

from typing import TYPE_CHECKING

from geant4_python_application.application import Message

if TYPE_CHECKING:
    from geant4_python_application.application import Application


class Generator:
    """Configure Geant4's particle gun or General Particle Source (GPS)."""

    def __init__(self, application: Application):
        self._application = application

    @property
    def type(self) -> str:
        return self._application._send_and_recv(Message("generator", "get_type", (), {}))

    @type.setter
    def type(self, generator_type: str):
        self._application._send_and_recv(
            Message("generator", "set_type", (generator_type,), {})
        )

    def use_gun(self) -> Generator:
        self.type = "gun"
        return self

    def use_gps(self) -> Generator:
        self.type = "gps"
        return self

    def particle(self, name: str) -> Generator:
        command = "/gps/particle" if self.type == "gps" else "/gun/particle"
        self._application.command(f"{command} {name}")
        return self

    def energy(self, value: float, unit: str = "MeV") -> Generator:
        command = "/gps/ene/mono" if self.type == "gps" else "/gun/energy"
        self._application.command(f"{command} {value} {unit}")
        return self

    def position(
        self, x: float, y: float, z: float, unit: str = "cm"
    ) -> Generator:
        if self.type == "gps":
            self._application.command("/gps/pos/type Point")
            self._application.command(f"/gps/pos/centre {x} {y} {z} {unit}")
        else:
            self._application.command(f"/gun/position {x} {y} {z} {unit}")
        return self

    def direction(self, x: float, y: float, z: float) -> Generator:
        command = "/gps/direction" if self.type == "gps" else "/gun/direction"
        self._application.command(f"{command} {x} {y} {z}")
        return self

    def commands(self, commands: list[str]) -> Generator:
        """Apply advanced source commands such as GPS distributions."""
        self._application.commands(commands)
        return self
