#!/bin/bash

# NOTE: THIS TAKES ABOUT 4 HOURS


echo "download data ......."

bash scripts/download_alphafold_params_s3.sh /fsx-shared/openfold/data/
bash scripts/download_mgnify_s3.sh /fsx-shared/openfold/data/
bash scripts/download_pdb_mmcif_s3.sh /fsx-shared/openfold/data/
bash scripts/download_small_bfd_s3.sh /fsx-shared/openfold/data/
bash scripts/download_uniprot_s3.sh /fsx-shared/openfold/data/
bash scripts/download_bfd_s3.sh /fsx-shared/openfold/data/
bash scripts/download_pdb70_s3.sh /fsx-shared/openfold/data/
bash scripts/download_pdb_seqres_s3.sh /fsx-shared/openfold/data/
bash scripts/download_uniclust30_s3.sh /fsx-shared/openfold/data/
bash scripts/download_uniref90_s3.sh /fsx-shared/openfold/data/

echo "***DONE***"


