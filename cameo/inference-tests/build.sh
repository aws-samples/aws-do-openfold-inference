#!/bin/bash

source ../../docker.properties

docker build -t ${registry}/cameo-inference -f Dockerfile .
