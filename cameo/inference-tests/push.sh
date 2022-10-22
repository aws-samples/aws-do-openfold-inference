#!/bin/bash

source ../../docker.properties

# Login to ECR

docker push ${registry}/cameo-inference
