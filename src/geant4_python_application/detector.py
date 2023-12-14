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
