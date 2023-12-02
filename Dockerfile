FROM python:3.11-slim-bullseye

RUN apt-get update -qq && apt-get install -q -y --no-install-recommends \
    build-essential ninja-build git curl libexpat-dev libxerces-c-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install a more recent CMake version
RUN pip install cmake

ARG CMAKE_CXX_STANDARD=20
ARG GEANT4_VERSION=v11.1.3

RUN git clone https://github.com/Geant4/geant4.git /tmp/geant4 --branch=${GEANT4_VERSION} --depth=1 \
    && cmake -G Ninja -B /tmp/geant4/build -S /tmp/geant4 \
    -DCMAKE_INSTALL_PREFIX=/opt/geant4 -DCMAKE_CXX_STANDARD=$CMAKE_CXX_STANDARD -DCMAKE_BUILD_TYPE=Release \
    -DGEANT4_USE_GDML=ON \
    -DGEANT4_INSTALL_EXAMPLES=OFF \
    -DGEANT4_INSTALL_DATA=OFF \
    -DGEANT4_BUILD_TLS_MODEL=global-dynamic \
    # -DGEANT4_USE_SYSTEM_EXPAT=OFF \
    # -DBUILD_STATIC_LIBS=ON \
    # -DBUILD_SHARED_LIBS=OFF \
    # -DGEANT4_BUILD_STORE_TRAJECTORY=OFF -DGEANT4_BUILD_VERBOSE_CODE=OFF \
    && cmake --build /tmp/geant4/build -j$(nproc) --target install \
    && rm -rf /tmp/geant4

ENV PATH=/opt/geant4/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/geant4/lib:$LD_LIBRARY_PATH

# RUN geant4-config --install-datasets

COPY . /source

# Build and install
RUN pip install /source && rm -rf /source
