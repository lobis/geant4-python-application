FROM ghcr.io/lobis/geant4-python-application:latest

ARG NB_USER=user
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

COPY ./examples ${HOME}/examples

USER root
RUN chown -R ${NB_UID} ${HOME}

# User needs to write to data directory (Install Geant4 datasets)
RUN data_dir=/opt/geant4/share/Geant4/data && mkdir -p $data_dir && chmod -R 777 $data_dir

USER ${NB_USER}

RUN pip install notebook jupyterlab

WORKDIR ${HOME}/examples

ENTRYPOINT []
