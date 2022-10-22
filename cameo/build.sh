#!/bin/bash

source ../docker.properties

docker image build -t ${registry}/cameo .
