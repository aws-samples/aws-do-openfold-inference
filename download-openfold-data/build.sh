#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

#!/bin/bash

source ../docker.properties

# Build Docker image
docker image build -t ${registry}/s3-fsx .
