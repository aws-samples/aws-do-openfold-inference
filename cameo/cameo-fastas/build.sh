#!/bin/bash

source ../../docker.properties

docker build -t ${registry}/temp-fasta -f Dockerfile .
