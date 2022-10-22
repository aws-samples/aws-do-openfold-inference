#!/bin/bash

source ../../docker.properties

#Login to ECR
docker push ${registry}/temp-fasta
