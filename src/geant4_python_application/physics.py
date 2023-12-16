from __future__ import annotations

from geant4_python_application import Application


class Physics:
    def __init__(self, application: Application):
        self._application = application
