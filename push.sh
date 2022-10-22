#!/bin/bash

source docker.properties

#Login to ECR

# Push Docker image
docker push ${registry}/openfold
