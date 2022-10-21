#!/bin/bash

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 999701187340.dkr.ecr.us-west-2.amazonaws.com

docker push 999701187340.dkr.ecr.us-west-2.amazonaws.com/temp-fasta
