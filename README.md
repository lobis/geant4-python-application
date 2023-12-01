# Geant4 Python Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lobis/geant4-python-application/HEAD)
[![Build and Test](https://github.com/lobis/geant4-python-application/actions/workflows/build-test.yml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/test.yml)
[![Docker Image](https://github.com/lobis/geant4-python-application/actions/workflows/docker.yml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/docker.yml)

```python
from geant4_python_application import Application, basic_gdml

app = Application()

app.setup_manager(n_threads=0)
app.setup_physics()
app.setup_detector(gdml=basic_gdml)
app.setup_action()

app.initialize()

print(f"Random seed: {app.random_seed}")

events = app.run(n_events=100)

print(events)
```
