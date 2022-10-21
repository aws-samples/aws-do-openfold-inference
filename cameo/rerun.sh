#!/bin/bash

kubectl delete -f cameo-yamls

./build.sh

./push.sh
