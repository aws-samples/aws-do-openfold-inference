#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

source docker.properties

#Login to ECR

# Push Docker image
docker push ${registry}/s3-fsx
