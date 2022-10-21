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
    if [ "$1" == "" ]; then
    test_container=0
        while [ $test_container -lt $num_test_containers ]; do
            CMD="docker rm -f ${test_image_name}-${test_container}"
            echo "$CMD"
            eval "$CMD"
            test_container=$((test_container+1))
        done
    else
        CMD="Docker rm -f ${test_image_name}-$1"
        echo "$CMD"
        eval "$CMD"
    fi
elif [ "$runtime" == "kubernetes" ]; then
    pushd ./5-test > /dev/null
    kubectl delete -f ${test_dir}
    popd > /dev/null
else
    echo "Runtime $runtime not recognized"
fi
