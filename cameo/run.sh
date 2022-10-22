#!/bin/bash

source ../docker.properties

docker run -it --gpus 0 ${registry}/cameo /bin/bash

