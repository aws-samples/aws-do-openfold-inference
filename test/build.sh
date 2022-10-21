#!/bin/bash

source ../inference_config.properties

docker build -t <ECR-registry-path>/test-openfold -f 5-test/Dockerfile .
