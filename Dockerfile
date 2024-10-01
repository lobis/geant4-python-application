FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip python-is-python3 git cmake build-essential libxerces-c-dev && apt-get clean

ENV Geant4_DIR=/geant4

RUN git clone https://github.com/Geant4/geant4.git /geant4-source --depth 1 --branch v11.2.2 && \
    cmake -B geant4-build -S geant4-source -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${Geant4_DIR} -DCMAKE_CXX_STANDARD=17 -DGEANT4_USE_GDML=ON  \
    -DGEANT4_INSTALL_EXAMPLES=OFF -DGEANT4_INSTALL_DATA=OFF -DGEANT4_BUILD_TLS_MODEL=global-dynamic -DBUILD_STATIC_LIBS=ON -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_C_FLAGS=-fPIC -DGEANT4_USE_SYSTEM_EXPAT=OFF && \
    cmake --build geant4-build --parallel $(nproc) --config Release --target install && \
    rm -rf geant4-source geant4-build

COPY . /src

RUN cd /src && pip install . --break-system-packages && cd / && rm -rf /src

WORKDIR /

ENTRYPOINT ["python"]
