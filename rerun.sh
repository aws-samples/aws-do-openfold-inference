#!/bin/bash

#kubectl delete -f ../run-openfold-inference/run-openfold-inference.yaml

source ./inference_config.properties

kubectl delete -f ./deploy/${app_dir}

./build.sh

./push.sh

./deploy.sh

