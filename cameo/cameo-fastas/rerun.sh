#!/bin/bash

kubectl delete -f temp-fasta.yaml

#source ./inference_config.properties

#kubectl delete -f ./deploy/${app_dir}

./build.sh

./push.sh


