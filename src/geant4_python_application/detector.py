from __future__ import annotations

from geant4_python_application import Application
from geant4_python_application.application import Message


class Detector:
    def __init__(self, application: Application):
        self._application = application

    def check_overlaps(self) -> Detector:
        return self._application._send_and_recv(
            Message("detector", "check_overlaps", (), {})
        )

    @property
    def gdml(self) -> str:
        return self._application._send_and_recv(Message("detector", "get_gdml", (), {}))

    @property
    def logical_volumes(self):
        return self._application._send_and_recv(
            Message("detector", "get_logical_volumes", (), {})
        )

    @property
    def physical_volumes(self):
        return self._application._send_and_recv(
            Message("detector", "get_physical_volumes", (), {})
        )

    @property
    def materials(self):
        return self._application._send_and_recv(
            Message("detector", "get_materials", (), {})
        )

    @property
    def sensitive_volumes(self):
        return self._application._send_and_recv(
            Message("detector", "get_sensitive_volumes", (), {})
        )

    @sensitive_volumes.setter
    def sensitive_volumes(self, volumes):
        self._application._send_and_recv(
            Message("detector", "set_sensitive_volumes", (volumes,), {})
        )

    @property
    def magnetic_field(self) -> tuple[float, float, float]:
        """Uniform global magnetic field vector in tesla."""
        return tuple(
            self._application._send_and_recv(
                Message("detector", "get_magnetic_field", (), {})
            )
        )

    @magnetic_field.setter
    def magnetic_field(self, field_tesla: tuple[float, float, float]):
        self._application._send_and_recv(
            Message("detector", "set_magnetic_field", (field_tesla,), {})
        )

    @property
    def electric_field(self) -> tuple[float, float, float]:
        """Uniform global electric field vector in kV/cm."""
        return tuple(
            self._application._send_and_recv(
                Message("detector", "get_electric_field", (), {})
            )
        )

    @electric_field.setter
    def electric_field(self, field_kv_per_cm: tuple[float, float, float]):
        self._application._send_and_recv(
            Message("detector", "set_electric_field", (field_kv_per_cm,), {})
        )

    def material_from_volume(self, volume: str) -> str:
        return self._application._send_and_recv(
            Message("detector", "get_material_from_volume", (volume,), {})
        )

    def logical_volume_from_physical(self, physical: str) -> str:
        return self._application._send_and_recv(
            Message(
                "detector", "get_logical_volume_from_physical_volume", (physical,), {}
            )
        )

    def physical_volumes_from_logical(self, logical: str) -> set[str]:
        return self._application._send_and_recv(
            Message(
                "detector", "get_physical_volumes_from_logical_volume", (logical,), {}
            )
        )
