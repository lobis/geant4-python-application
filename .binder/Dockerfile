FROM continuumio/miniconda3:main

# install conda deps (auto y)
RUN conda install --yes -c conda-forge gxx_linux-64 cmake geant4=11.2.2 matplotlib jupyterlab

COPY . /src

RUN cd /src && export CXX=$(which g++) && pip install . && rm -rf /src

ARG NB_USER=user
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

COPY ./examples/*.ipynb ${HOME}/
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

WORKDIR ${HOME}
