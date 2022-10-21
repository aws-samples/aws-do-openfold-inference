#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

# Pull model image from container registry

if [ -f ./inference_config.properties ]; then
    source ./inference_config.properties
elif [ -f ../inference_config.properties ]; then
    source ../inference_config.properties
else
    echo "config.properties not found!"
fi

docker pull 999701187340.dkr.ecr.us-west-2.amazonaws.com/test-openfold
