#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

#Login to ECR

# Push Docker image
docker push <ECR-registry-path>/s3-fsx
