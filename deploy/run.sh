#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################


source ../inference_config.properties
echo "Processor: $processor"

#kubectl create namespace ${namespace} --dry-run=client -o yaml | kubectl apply -f -
./generate-yaml.sh
kubectl apply -f ${app_dir}
