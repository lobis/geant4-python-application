FROM continuumio/miniconda3:latest

# Install dependencies and upgrade
RUN apt-get update -qq && apt-get install -q -y --no-install-recommends \
    build-essential ninja-build curl vim libxerces-c-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Need a more recent version of cmake
RUN conda install -y cmake && conda clean -y --all

ARG CMAKE_CXX_STANDARD=20
ARG GEANT4_VERSION=v11.1.3

RUN git clone https://github.com/Geant4/geant4.git /tmp/geant4 --branch=${GEANT4_VERSION} --depth=1 \
    && cmake -G Ninja -B /tmp/geant4/build -S /tmp/geant4 -DCMAKE_INSTALL_PREFIX=/usr/local/ \
    -DCMAKE_CXX_STANDARD=$CMAKE_CXX_STANDARD -DGEANT4_INSTALL_EXAMPLES=OFF -DGEANT4_USE_GDML=ON \
    -DGEANT4_INSTALL_DATA=OFF \
    # -DGEANT4_BUILD_STORE_TRAJECTORY=OFF -DGEANT4_BUILD_VERBOSE_CODE=OFF \
    && cmake --build /tmp/geant4/build -j$(nproc) --target install \
    && rm -rf /tmp/geant4

# RUN geant4-config --install-datasets

COPY . /source

# Build and install
RUN pip install /source && rm -rf /source

ENTRYPOINT ["python"]
