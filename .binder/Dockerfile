FROM ghcr.io/lobis/geant4:latest

ARG NB_USER=user
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

RUN mamba install -y \
    notebook jupyterlab \
    && mamba clean -ya

COPY ./examples ${HOME}/examples
USER root
RUN chown -R ${NB_UID} ${HOME}

USER ${NB_USER}

RUN /opt/conda/bin/conda init bash \
    && /opt/conda/bin/conda config --set auto_activate_base true

ENTRYPOINT []
