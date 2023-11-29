FROM ubuntu:latest

# Install dependencies and upgrade
RUN apt-get update && apt-get install -y \
    build-essential bzip2 ca-certificates curl mesa-common-dev libglu1-mesa-dev python3-dev \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install miniconda and activate base on startup
RUN curl -o miniconda_installer.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash miniconda_installer.sh -b -p /opt/conda \
    && rm miniconda_installer.sh \
    && /opt/conda/bin/conda install -y -c conda-forge mamba \
    && /opt/conda/bin/conda init bash \
    && /opt/conda/bin/conda config --set auto_activate_base true \
    && /opt/conda/bin/conda clean -ya

# Install conda packages (geant4 is not available for aarch64 at the time of writing)
RUN /opt/conda/bin/mamba install -y -c conda-forge cmake geant4 \
    && /opt/conda/bin/conda clean -ya

SHELL [ "/bin/bash", "-c" ]

# Set python as the entrypoint
ENTRYPOINT [ "/opt/conda/bin/python3" ]
