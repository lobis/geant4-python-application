FROM ubuntu:latest

# Install dependencies and upgrade
RUN apt-get update && apt-get install -y \
    build-essential bzip2 ca-certificates curl git mesa-common-dev libglu1-mesa-dev python3-dev \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install miniconda and activate base on startup
ENV PATH /opt/conda/bin:/opt/conda/condabin:${PATH}
ENV CMAKE_PREFIX_PATH=/opt/conda

RUN curl -o miniconda_installer.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash miniconda_installer.sh -b -p /opt/conda \
    && rm miniconda_installer.sh \
    && conda install -y -c conda-forge mamba \
    && mamba init bash \
    && mamba config --set auto_activate_base true \
    && mamba clean -ya

# Install conda packages (geant4 is not available for aarch64 at the time of writing)
RUN mamba install -y -c conda-forge  \
    cmake geant4 \
    && mamba clean -ya

# Copy files
COPY . /source

# Build and install
RUN cd source && python -m pip install .

# ENV PYTHONPATH=/opt/conda/lib:${PYTHONPATH}

RUN echo "#!/bin/bash\nexec /opt/conda/bin/conda run --no-capture-output -n base /opt/conda/bin/python \"\$@\"" > /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh

# Set the entry point to the script
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
