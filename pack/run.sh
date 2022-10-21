#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

conda run --no-capture-output -n openfold_venv hypercorn fastapi-server:app -b 0.0.0.0:8080
