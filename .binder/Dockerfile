FROM ghcr.io/lobis/geant4:latest

RUN /opt/conda/bin/pip install --no-cache-dir notebook jupyterlab

ARG NB_USER=user
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Override the default entrypoint
ENTRYPOINT []
