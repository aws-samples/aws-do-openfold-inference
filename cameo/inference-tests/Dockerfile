FROM ubuntu:20.04

RUN apt-get update && apt-get install -y htop vim wget curl software-properties-common debconf-utils python3-distutils dnsutils bc

# Install python3.9
RUN DEBIAN_FRONTEND=noninteractive; add-apt-repository -y ppa:deadsnakes/ppa; apt install -y python3.9; update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1

# Install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; python get-pip.py; rm -f get-pip.py

# Install other python libraries
RUN pip install pandas requests sockets 

RUN mkdir /app/

COPY . /app

#CMD ["bash","-c","while true; do date; sleep 10; done"]

ENTRYPOINT ["python", "/app/cameo-inference-test.py"]
