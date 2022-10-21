FROM ubuntu:20.04

RUN apt-get update
RUN apt -y upgrade 
RUN apt-get install -y curl unzip rsync

#Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install

#Remove aws cli artifacts after installation
RUN rm -rf aws && rm awscliv2.zip

#Install aria2
RUN apt-get --fix-missing install -y aria2

WORKDIR /workspace

#Add openfold
COPY ./scripts /workspace/scripts

ADD data-prep.sh /workspace/
RUN chmod +x /workspace/data-prep.sh

#ADD model-save.sh /
#RUN chmod +x /data-prep.sh
