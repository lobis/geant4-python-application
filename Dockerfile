FROM ubuntu:latest

# Install dependencies and upgrade
RUN apt-get update && apt-get install -y \
    build-essential bzip2 ca-certificates curl git mesa-common-dev libglu1-mesa-dev python3-dev \
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

# Copy files
COPY . /source

# Build and install
RUN cd /source/application \
    && mkdir build \
    && cd build \
    && /opt/conda/bin/cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/conda -DCMAKE_INSTALL_PREFIX=/opt/conda \
    && make -j$(nproc) \
    && make install \
    && cd /source \
    && /opt/conda/bin/pip install . \
    && rm -rf /source

ENV PYTHONPATH=/opt/conda/lib:${PYTHONPATH}

RUN echo "#!/bin/bash\nexec /opt/conda/bin/conda run --no-capture-output -n base /opt/conda/bin/python \"\$@\"" > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Set the entry point to the script
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
