# Geant4 Pythonic Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lobis/geant4-pythonic-application/HEAD)
[![Build and Test](https://github.com/lobis/geant4-pythonic-application/actions/workflows/test.yml/badge.svg)](https://github.com/lobis/geant4-pythonic-application/actions/workflows/test.yml)
[![Build and Publish the Docker Image](https://github.com/lobis/geant4-pythonic-application/actions/workflows/docker.yml/badge.svg)](https://github.com/lobis/geant4-pythonic-application/actions/workflows/docker.yml)

```python
from geant4 import Application

app = Application()

app.random_seed = 0
app.setup_manager(n_threads=0)
app.setup_physics()
app.setup_detector()  # can take a GDML string as argument
app.setup_action()

app.initialize()

# if the seed is set to 0, the seed will be randomized
print(f"Random seed: {app.random_seed}")

# launch 100 events
events = app.run(100)
```
