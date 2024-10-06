FROM python:3.12-slim-bookworm as build

RUN apt-get update && apt-get install -y python3 python3-pip python-is-python3 git cmake build-essential && apt-get clean

ENV Geant4_DIR=/geant4

RUN git clone https://github.com/apache/xerces-c.git xerces-source && \
    git -C xerces-source checkout tags/v3.2.5 && \
    cmake -B xerces-build -S xerces-source -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/xerces -DCMAKE_CXX_STANDARD=17 -DBUILD_SHARED_LIBS=OFF -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_C_FLAGS=-fPIC -Dnetwork-accessor=socket -Dtranscoder=iconv && \
    cmake --build xerces-build --parallel $(nproc) --config Release --target install

RUN git clone https://github.com/Geant4/geant4.git /geant4-source --depth 1 --branch v11.2.2 && \
    cmake -B geant4-build -S geant4-source -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${Geant4_DIR} -DCMAKE_CXX_STANDARD=17 -DGEANT4_USE_GDML=ON  \
    -DGEANT4_INSTALL_EXAMPLES=OFF -DGEANT4_INSTALL_DATA=OFF -DGEANT4_BUILD_TLS_MODEL=global-dynamic -DBUILD_STATIC_LIBS=ON -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_C_FLAGS=-fPIC -DGEANT4_USE_SYSTEM_EXPAT=OFF -DXERCESC_ROOT_DIR=/xerces && \
    cmake --build geant4-build --parallel $(nproc) --config Release --target install && \
    rm -rf geant4-source geant4-build

COPY . /src

RUN cd /src && pip install . --target=/install && cd / && rm -rf /src

FROM python:3.12-slim-bookworm

COPY --from=build /install /usr/local/lib/python3.12/site-packages

ENTRYPOINT ["python3"]
