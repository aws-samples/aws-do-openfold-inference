FROM public.ecr.aws/lts/ubuntu:18.04_stable as base_image

SHELL ["/bin/bash", "-c"]

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      build-essential \
      cmake \
      wget \
      git \
      unzip \
      hmmer \
      tar \
      awscli \
      python3.7 \
      python3-pip \
    && apt-get clean \
    && rm /usr/bin/python3 \
    && ln -s /usr/bin/python3.7 /usr/bin/python3 \
    && rm -rf /var/lib/apt/lists/*

# Compile HHsuite from source.
RUN git clone --branch v3.3.0 https://github.com/soedinglab/hh-suite.git /tmp/hh-suite \
    && mkdir /tmp/hh-suite/build \
    && pushd /tmp/hh-suite/build \
    && cmake -DCMAKE_INSTALL_PREFIX=/opt/hhsuite .. \
    && make && make install \
    && ln -s /opt/hhsuite/bin/* /usr/bin \
    && popd
    # && rm -rf /tmp/hh-suite    

# Compile kalign2 from source
RUN wget http://msa.sbc.su.se/downloads/kalign/current.tar.gz \
  && mkdir -p /tmp/kalign2/build \
  && tar -xvzf current.tar.gz -C /tmp/kalign2 \
  && pushd /tmp/kalign2 \
  && ./configure \
  && make && make install \
  && mv /usr/local/bin/kalign /usr/bin/kalign \
  && popd \
  && rm -rf /tmp/kalign2

COPY . /opt/msa

RUN git clone --depth 1 https://github.com/aqlaboratory/openfold.git /opt/msa

WORKDIR /opt/msa

RUN pip3 install --upgrade pip \
    && python3 -m pip install -r /opt/msa/requirements.txt 

#ENTRYPOINT ["bash", "-c"]
ENTRYPOINT ["python3","precompute_alignments.py"]
