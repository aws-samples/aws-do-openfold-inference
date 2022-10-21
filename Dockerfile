FROM nvidia/cuda:11.1.1-devel-ubuntu20.04

LABEL description="Base container for OpenFold"


RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

#RUN apt-get update && apt-get install -y wget libxml2 cuda-minimal-build-11-3 libcusparse-dev-11-3 git

RUN apt-get update && apt-get install -y wget git vim

RUN wget -P /tmp \
    "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh" \
    && bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda \
    && rm /tmp/Miniconda3-latest-Linux-x86_64.sh
ENV PATH /opt/conda/bin:$PATH

RUN git clone --depth 1 https://github.com/aqlaboratory/openfold.git /opt/

COPY ./environment.yml /opt/openfold/environment.yml
COPY ./pack/fastapi-server.py /opt/openfold/fastapi-server.py
COPY ./inference_config.properties /opt/openfold/inference_config.properties
COPY ./pack/run.sh /opt/openfold/run.sh
COPY ./inference_test.py /opt/openfold/inference_test.py
COPY ./requirements.txt /opt/openfold/requirements.txt

# installing into the base environment since the docker container wont do anything other than run openfold
RUN conda env update -n base --file /opt/openfold/environment.yml && conda clean --all


RUN wget -q -P /opt/openfold/openfold/resources \
    https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt
RUN patch -p0 -d /opt/conda/lib/python3.7/site-packages/ < /opt/openfold/lib/openmm.patch
WORKDIR /opt/openfold

RUN echo "PATH=/usr/local/cuda/bin\${PATH:+:\${PATH}}" >> /etc/environment
RUN echo "LD_LIBRARY_PATH=/usr/local/cuda/lib64\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}" >> /etc/environment


RUN conda env create -f /opt/openfold/environment.yml

SHELL ["conda", "run", "-n", "openfold_venv", "/bin/bash", "-c"]

RUN python3 setup.py install
RUN pip install -r requirements.txt

USER root
#ENTRYPOINT ["conda", "run", "--no-capture-output" ,"-n", "openfold_venv", "python3","/opt/openfold/run_pretrained_openfold.py"]

EXPOSE 8080

CMD ["./run.sh"]


