FROM python:3.12-slim-bullseye as builder

RUN python -m pip install --no-cache-dir geant4-python-application

ENTRYPOINT ["python"]
