#!/bin/bash

######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

if [ -f ../inference_config.properties ]; then
    source ../inference_config.properties
elif [ -f ../../inference_config.properties ]; then
    source ../../inference_config.properties
elif [ -f ./inference_config.properties ]; then
    source ./inference_config.properties
else
    echo "config.properties not found!"
fi

server=0
servers=$num_servers
model=0
models=$num_models

# get instance ip addresses
rm -f  ./endpoint_ip.conf
while [ $server -lt $servers ]
do
	if [ "$runtime" == "docker" ]; then
		server_ip=$(cat /etc/hosts | grep ${app_name}-${server} | awk '{print $1}')
	elif [ "$runtime" == "kubernetes" ]; then
		server_ip=$(host ${app_name}-${server}.${test_namespace}.svc.cluster.local | grep "has address" | cut -d ' ' -f 4)
	fi
	echo $server_ip >> ./endpoint_ip.conf
	server=$((server+1))
done

echo "Endpoints:"
cat ./endpoint_ip.conf

mapfile -t server_ips < endpoint_ip.conf 

server_last_index=$((${#server_ips[@]}-1))
model_last_index=$(($models-1))
request=0
while [ $request -lt $num_requests ]
do
	server=$(shuf -i 0-${server_last_index} -n 1)
	server_ip=${server_ips[$server]}
	model=$(shuf -i 0-${model_last_index} -n 1)
	echo "Request: $request, Server: $server, IP: $server_ip,  Model: $model"
	./clock.sh curl http://$server_ip:8080/openfold_predictions/model_$model
	sleep $request_frequency
	request=$((request+1))
done

rm -f  ./endpoint_ip.conf
