FROM python:3.11-slim-bullseye as builder

RUN apt-get update -qq && apt-get install -q -y --no-install-recommends \
    build-essential ninja-build git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install a more recent CMake version
RUN pip install cmake

ARG CMAKE_CXX_STANDARD=23
ARG GEANT4_VERSION=11.1.3
ARG XERCES_VERSION=3.2.4

RUN git clone https://github.com/apache/xerces-c.git /tmp/xerces \
    && git -C /tmp/xerces checkout tags/v${XERCES_VERSION} \
    && cmake -G Ninja -B /tmp/xerces/build -S /tmp/xerces \
    -DCMAKE_INSTALL_PREFIX=/opt/xerces \
    -DCMAKE_CXX_STANDARD=23 \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -Dnetwork-accessor=socket \
    -Dtranscoder=iconv \
    -DCMAKE_CXX_FLAGS=-fPIC \
    -DCMAKE_C_FLAGS=-fPIC \
    && cmake --build /tmp/xerces/build -j$(nproc) --target install \
    && rm -rf /tmp/xerces

RUN git clone https://github.com/Geant4/geant4.git /tmp/geant4 --branch=v${GEANT4_VERSION} --depth=1 \
    && cmake -G Ninja -B /tmp/geant4/build -S /tmp/geant4 \
    -DCMAKE_INSTALL_PREFIX=/opt/geant4 \
    -DXERCESC_ROOT_DIR=/opt/xerces \
    -DCMAKE_CXX_STANDARD=23 \
    -DCMAKE_BUILD_TYPE=Release \
    -DGEANT4_USE_GDML=ON \
    -DGEANT4_INSTALL_EXAMPLES=OFF \
    -DGEANT4_INSTALL_DATA=OFF \
    -DGEANT4_BUILD_TLS_MODEL=global-dynamic \
    -DCMAKE_CXX_FLAGS=-fPIC \
    -DCMAKE_C_FLAGS=-fPIC \
    -DGEANT4_USE_SYSTEM_EXPAT=OFF \
    -DBUILD_STATIC_LIBS=ON \
    -DBUILD_SHARED_LIBS=OFF \
    && cmake --build /tmp/geant4/build -j$(nproc) --target install \
    && rm -rf /tmp/geant4

COPY . /source

# Build and install
RUN source /opt/geant4/bin/geant4.sh \
    && pip install /source \
    && rm -rf /source

# Create the final image
FROM python:3.11-slim-bullseye

# Copy installed Python package from the builder image
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

ENTRYPOINT ["python"]
