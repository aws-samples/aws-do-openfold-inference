## AWS EKS Architecture For OpenFold Inference

# 1. Overview
OpenFold, developed by Columbia University, is an open-source protein structure prediction model implemented with PyTorch. OpenFold is a faithful reproduction of the Alphafold2 protein structure prediction model, while delivering performance improvements over AlphaFold2. It contains a number of training and inference specific optimizations that take advantage of different memory-time tradeoffs for different protein lengths based on model training or inference runs. For training, OpenFold supports FlashAttention optimizations that accelerate the mutli sequence alignment (MSA) attention component. FlashAttention optimizations along with JIT compilation accelerate the inference pipeline delivering twice the performance for shorter protein sequences than AlphaFold2.

Columbia University has publicly released the model weights and training data consisting of 400,000 Multiple Sequence Alignments (MSAs) and PDB70 template hit files under a permissive license. Model weights are available via scripts in the [GitHub repository](https://github.com/aqlaboratory/openfold/blob/main/README.md) while the MSAs are hosted by the [Registry of Open Data on AWS (RODA)](https://registry.opendata.aws/openfold/). Using Python and Pytorch for implementation allows OpenFold to have access to a large array of ML modules and developers, thus ensuring its continued improvement and optimization.

In this repo, we will show how you can deploy OpenFold models on Amazon EKS and how to scale the EKS clusters to drastically reduce multi-sequence alignment (MSA) computation and protein structure inference times. We will show the performance of this architecture to run alignment computation and inference on the popular open source Cameo dataset. Running this workload end to end on all 92 proteins available in the [Cameo](https://www.cameo3d.org/) dataset would take a total of 8 hours which includes downloading the required data, alignment computation and inference times. Figure 1 shows sample EKS architecture for inference with OpenFold.

![Architecture](https://github.com/aws-samples/aws-do-openfold-inference/blob/main/Achitecture.png?raw=true 'TITLE')


# 2. Prerequisites
It is assumed that an EKS cluster exists and contains nodegroups of the desired target instance types. You can use this [repo](https://github.com/aws-samples/aws-do-eks) to create the cluster. [aws-do-eks](https://github.com/aws-samples/aws-do-eks) also includes steps to create and mount an FSx for Lustre volume on an EKS cluster [here](https://github.com/aws-samples/aws-do-eks/tree/main/Container-Root/eks/deployment/csi/fsx). Also update docker.properties with your ECR registry path.

# 3. Download OpenFold Data
The [download-openfold-data](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/download-openfold-data) folder contains all the necessary scripts to download data from S3 buckets s3://aws-batch-architecture-for-alphafold-public-artifacts/ and s3://pdbsnapshots/ into the FSx for Lustre
file system. To download data, cd into the download-openfold-data folder and update <ECR-registry-path> and run `./build.sh` to build the Docker image and do the same for `./push.sh`. Once that is done run `kubectl apply -f fsx-data-prep-pod.yaml` to kickstart jobs to download data. Clone OpenFold model files from https://huggingface.co/nz/OpenFold and download them into an S3 bucket and from there into an FSx for Lustre file system using the above steps. 
  
# 4. Run OpenFold Inference
Once the data and model files are downloaded, the [run-openfold-inference](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/run-openfold-inference) provides all the scripts necessary to run [run-pretrained-openfold.py] (https://github.com/aqlaboratory/openfold/blob/main/run_pretrained_openfold.py) script on EKS. Follow the `./build.sh` and `./push.sh` scripts to build and push docker images to ECR. You can start an inference pod by running `kubectl apply -f run-openfold-inference.yaml`.
  
# 5. Deploy OpenFold Models as APIs
The [inference_config.properties](https://github.com/aws-samples/aws-do-openfold-inference/blob/main/inference_config.properties) file gives you a configuration script to specify openfold parameters and hardware specifications that you would use to pack OpenFold models in a container and deploy it. In addition to this config, the [pack](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/pack) folder exposes alignment computation and inference calls from [run-pretrained-openfold.py] (https://github.com/aqlaboratory/openfold/blob/main/run_pretrained_openfold.py) as apis using the fast-api framework [here](https://github.com/aws-samples/aws-do-openfold-inference/blob/main/pack/fastapi-server.py). Run the `./deploy.sh` script to deploy models on EKS.
  
# 6. Alignment Computation
In this repo, we share an example where we run alignment computation on all 92 proteins available in the [Cameo](https://www.cameo3d.org/) dataset. The [cameo](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/cameo) folder contains all scripts necessary for alignment computation and inference tests on the [Cameo](https://www.cameo3d.org/) dataset. Please follow the following steps to set up alignment computation jobs on EKS:
  
a. Build and push docker image in the [cameo-fastas](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/cameo/cameo-fastas) folder and run `kubectl apply -f temp-fasta.yaml` to preprocess the Cameo data into individual fasta files per protein sequence in FSx for Lustre file system.
b. Run [run-grid.py](https://github.com/aws-samples/aws-do-openfold-inference/blob/main/cameo/run-grid.py) code that will use [run-cameo.yaml](https://github.com/aws-samples/aws-do-openfold-inference/blob/main/cameo/run-cameo.yaml) as template to create 92 yaml files, one for each protein sequence) and save it in a `cameo-yamls` folder
c. Run `kubectl apply -f cameo-yamls` to kick off 92 alignment computation pods
  
# 7. Inference with OpenFold APIs
The [inference-tests](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/cameo/inference-tests) folder contains all the scripts necessary to call OpenFold Model APIs and run inference.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information. Prior to any production deployment, customers should work with their local security teams to evaluate any additional controls

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

