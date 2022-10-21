## AWS EKS Architecture For OpenFold Inference

# 1. Overview
OpenFold, developed by Columbia University, is an open-source protein structure prediction model implemented with PyTorch. OpenFold is a faithful reproduction of the Alphafold2 protein structure prediction model, while delivering performance improvements over AlphaFold2. It contains a number of training- and inference-specific optimizations that take advantage of different memory-time tradeoffs for different protein lengths based on model training or inference runs. For training, OpenFold supports FlashAttention optimizationsthat accelerate the mutli sequence alignment (MSA) attention component. FlashAttention optimizations along with JIT compilation accelerate the inference pipeline delivering twice the performance for shorter protein sequences than AlphaFold2.

Columbia University has publicly released the model weights and training data consisting of 400,000 Multiple Sequence Alignments (MSAs) and PDB70 template hit files under a permissive license. Model weights are available via scripts in the [GitHub repository](https://github.com/aqlaboratory/openfold/blob/main/README.md) while the MSAs are hosted by the [Registry of Open Data on AWS (RODA)](https://registry.opendata.aws/openfold/). Using Python and Pytorch for implementation allows OpenFold to have access to a large array of ML modules and developers, thus ensuring its continued improvement and optimization.

In this repo, we will show how you can deploy OpenFold models on Amazon EKS and how to scale the EKS clusters to drastically reduce multi-sequence alignment (MSA) computation and protein structure inference times.We will show the performance of this architecture to run alignment computation and inference on the popular open source Cameo dataset. Running this workload end to end on all 92 proteins available in the [Cameo](https://www.cameo3d.org/) dataset would take a total of 8 hours which includes downloading the required data, alignment computation and inference times. 

# 2. Prerequisites
It is assumed that an EKS cluster exists and contains nodegroups of the desired target instance types. You can use this [repo](https://github.com/aws-samples/aws-do-eks) to create the cluster. [aws-do-eks](https://github.com/aws-samples/aws-do-eks) also includes steps to create and mount an FSx for Lustre volume on an EKS cluster [here](https://github.com/aws-samples/aws-do-eks/tree/main/Container-Root/eks/deployment/csi/fsx)

# 3. Download OpenFold Data
The [download-openfold-data](https://github.com/aws-samples/aws-do-openfold-inference/tree/main/download-openfold-data) folder contains all the necessary scripts to download data from S3 buckets s3://aws-batch-architecture-for-alphafold-public-artifacts/ and s3://pdbsnapshots/ into the FSx for Lustre
file system. 


TODO: Fill this README out!

Be sure to:

* Change the title in this README
* Edit your repository description on GitHub

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information. Prior to any production deployment, customers should work with their local security teams to evaluate any additional controls

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

