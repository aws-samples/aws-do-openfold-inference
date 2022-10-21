#Login
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <ECR-registry-path>

# Push Docker image
docker push <ECR-registry-path>/openfold
