#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

if [ -f ../inference_config.properties ]; then
    source ../inference_config.properties
elif [ -f ./inference_config.properties ]; then
    source ./inference_config.properties
else
    echo "config.properties not found!"
fi

echo ""
echo "Runtime: $runtime"
echo "Processor: $processor"

if [ "$runtime" == "docker" ]; then
    CMD="docker ps -a | grep ${test_image_name}-"
    echo "$CMD"
    eval "$CMD"
elif [ "$runtime" == "kubernetes" ]; then
    if [ "$1" == "" ]; then
        echo ""
        echo "Pods:"
        kubectl -n ${test_namespace} get pods
    else
        echo ""
        echo "Pod:"
        kubectl -n ${test_namespace} get pod $(kubectl -n ${test_namespace} get pods | grep ${test_image_name}-$1 | cut -d ' ' -f 1) -o wide
    fi
else
    echo "Runtime $runtime not recognized"
fi
