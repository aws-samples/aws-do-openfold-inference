#!/bin/bash

kubectl delete -f fsx-data-prep-pod.yaml

./build.sh

./push.sh

kubectl apply -f fsx-data-prep-pod.yaml
