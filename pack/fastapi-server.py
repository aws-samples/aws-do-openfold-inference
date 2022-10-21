from datetime import date
import logging
import math
import numpy as np
import os

import pickle

import random
import sys
import time
import torch
import re

torch_versions = torch.__version__.split(".")
torch_major_version = int(torch_versions[0])
torch_minor_version = int(torch_versions[1])
if(
    torch_major_version > 1 or
    (torch_major_version == 1 and torch_minor_version >= 12)
):
    # Gives a large speedup on Ampere-class GPUs
    torch.set_float32_matmul_precision("high")

torch.set_grad_enabled(False)

from openfold.config import model_config, NUM_RES
from openfold.data import templates, feature_pipeline, data_pipeline
from openfold.model.model import AlphaFold
from openfold.model.torchscript import script_preset_
from openfold.np import residue_constants, protein
import openfold.np.relax.relax as relax
from openfold.utils.import_weights import (
    import_jax_weights_,
)
from openfold.utils.tensor_utils import (
    tensor_tree_map,
)

TRACING_INTERVAL = 50


#Fast api imports
from typing import Optional
from fastapi import FastAPI,responses
from configparser import ConfigParser
import boto3
import subprocess

# Global variables

global model
global logger
global config_preset
global model_name
global processor
global s3bucket
global use_precomputed_alignments
global alignment_dir
global skip_relaxation
global output_dir_base
global config
global template_featurizer
global data_processor
global feature_processor
global device_type
global device
global multimer_ri_gap
global no_cpus

def download_from_s3(s3bucket,remoteDirectoryName,destination_folder):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(s3bucket)
    for obj in bucket.objects.filter(Prefix = remoteDirectoryName):
        destination_path = destination_folder + os.path.dirname(obj.key)
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        bucket.download_file(obj.key, destination_path+'/'+obj.key.split('/')[-1]) # save to same path

def prep_output(out, batch, feature_dict, feature_processor):
    plddt = out["plddt"]
    mean_plddt = np.mean(plddt)

    plddt_b_factors = np.repeat(
        plddt[..., None], residue_constants.atom_type_num, axis=-1
    )

    #if(args.subtract_plddt):
    #    plddt_b_factors = 100 - plddt_b_factors

    # Prep protein metadata
    template_domain_names = []
    template_chain_index = None
    if(feature_processor.config.common.use_templates and "template_domain_names" in feature_dict):
        template_domain_names = [
            t.decode("utf-8") for t in feature_dict["template_domain_names"]
        ]

        # This works because templates are not shuffled during inference
        template_domain_names = template_domain_names[
            :feature_processor.config.predict.max_templates
        ]

        if("template_chain_index" in feature_dict):
            template_chain_index = feature_dict["template_chain_index"]
            template_chain_index = template_chain_index[
                :feature_processor.config.predict.max_templates
            ]

    no_recycling = feature_processor.config.common.max_recycling_iters
    remark = ', '.join([
        f"no_recycling={no_recycling}",
        f"max_templates={feature_processor.config.predict.max_templates}",
        f"config_preset={config_preset}",
    ])

    # For multi-chain FASTAs
    ri = feature_dict["residue_index"]
    chain_index = (ri - np.arange(ri.shape[0])) / multimer_ri_gap
    chain_index = chain_index.astype(np.int64)
    cur_chain = 0
    prev_chain_max = 0
    for i, c in enumerate(chain_index):
        if(c != cur_chain):
            cur_chain = c
            prev_chain_max = i + cur_chain * multimer_ri_gap

        batch["residue_index"][i] -= prev_chain_max

    unrelaxed_protein = protein.from_prediction(
        features=batch,
        result=out,
        b_factors=plddt_b_factors,
        chain_index=chain_index,
        remark=remark,
        parents=template_domain_names,
        parents_chain_index=template_chain_index,
    )

    return unrelaxed_protein


# Dictionaries
models = {}

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(level=logging.INFO)

path_prefix = os.path.dirname(__file__)
with open('./inference_config.properties') as f:
    inference_config_lines = '[global]\n' + f.read()
    f.close()
inference_config = ConfigParser()
inference_config.read_string(inference_config_lines)

model_name = inference_config['global']['openfold_model_name']
processor = inference_config['global']['processor']
s3bucket = inference_config['global']['s3bucket']
output_dir_base =  inference_config['global']['output_dir_base']
alignment_dir =  inference_config['global']['alignment_dir']
config_preset = inference_config['global']['config_preset']
use_precomputed_alignments = inference_config['global']['use_precomputed_alignments']
skip_relaxation = inference_config['global']['skip_relaxation']
# Default multimer_ri_gap value
multimer_ri_gap = 200
no_cpus = inference_config['global']['no_cpus']

# Detect runtime device type inf,gpu, or cpu
device_type=""
try:
    import torch_neuron
    device_type="inf"
except ImportError:
    logger.warning("Inferentia chip not detected")
    pass

if device_type == "inf":
    pass
elif torch.cuda.is_available():
    device_type="gpu"
    device = torch.device("cuda:0")
    logger.warning(torch.cuda.get_device_name(0))
else:
    device_type="cpu"
    device = torch.device(device_type)

if processor != device_type:
    logger.warning(f"Configured target processor {processor} differs from actual processor {device_type}")
logger.warning(f"Running models on processor: {device_type}")



num_models=1
try:
    num_models=int(os.getenv("NUM_MODELS", '1'))
except ValueError:
    logger.warning(f"Failed to parse environment variable NUM_MODELS={os.getenv('NUM_MODELS')}")
    logger.warning("Please ensure if set NUM_MODELS is a numeric value. Assuming value of 1")


# Create the output directory
#output_dir_base = '/fsx-shared/openfold/output_dir_EKS'
if not os.path.exists(output_dir_base):
    os.makedirs(output_dir_base, exist_ok=True)

# Create config
config = model_config(config_preset)

template_featurizer = templates.TemplateHitFeaturizer(
        mmcif_dir="/fsx-shared/openfold/data/pdb_mmcif/mmcif_files/",
        max_template_date = date.today().strftime("%Y-%m-%d"),
        max_hits=config.data.predict.max_templates,
        kalign_binary_path="/opt/conda/envs/openfold_venv/bin/kalign"
    )

data_processor = data_pipeline.DataPipeline(
        template_featurizer=template_featurizer,
    )


random_seed = random.randrange(2**32)
np.random.seed(random_seed)
torch.manual_seed(random_seed + 1)

feature_processor = feature_pipeline.FeaturePipeline(config.data)

if use_precomputed_alignments is None:
    alignment_dir = os.path.join(output_dir_base, "alignments")
#else:
    # Do nothing if alignments are in FSX
#    download_from_s3(s3bucket= s3bucket,remoteDirectoryName= use_precomputed_alignments,destination_folder = '/fsx-shared/openfold/output_dir_EKS/')
 #   alignment_dir = os.path.join(output_dir_base, "alignments")


default_tag = 'seq0'
default_seq = 'MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH'


# FastAPI server
app = FastAPI()

# Server healthcheck
@app.get("/")
async def root():
    return {"Status": "Healthy"}

# Pre-compute alignment API endpoint
@app.get("/precompute_alignments/")
async def infer(tag: Optional[str] = default_tag, seq: Optional[str] = default_seq):
    tag = tag
    seq = seq
    status = 200

    logger.info(f"Generating alignments for {tag}...")

    tmp_fasta_path = os.path.join(output_dir_base, f"tmp_{os.getpid()}.fasta")
    with open(tmp_fasta_path, "w") as fp:
        fp.write(f">{tag}\n{seq}")

    local_alignment_dir = os.path.join(alignment_dir, tag)
    if not os.path.exists(local_alignment_dir):
        os.makedirs(local_alignment_dir, exist_ok=True)

        alignment_runner = data_pipeline.AlignmentRunner(
                jackhmmer_binary_path='/opt/conda/envs/openfold_venv/bin/jackhmmer',
                hhblits_binary_path='/opt/conda/envs/openfold_venv/bin/hhblits',
                hhsearch_binary_path='/opt/conda/envs/openfold_venv/bin/hhsearch',
                uniref90_database_path='/fsx-shared/openfold/data/uniref90/uniref90.fasta',
                mgnify_database_path='/fsx-shared/openfold/data/mgnify/mgy_clusters_2018_12.fa',
                bfd_database_path='/fsx-shared/openfold/data/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt',
                uniclust30_database_path='/fsx-shared/openfold/data/uniclust30/uniclust30_2018_08/uniclust30_2018_08',
                pdb70_database_path='/fsx-shared/openfold/data/pdb70/pdb70',
                no_cpus=no_cpus
            )
        alignment_runner.run(tmp_fasta_path, local_alignment_dir)

        answer_text = f"Alignments for {tag} done..."
    else:
        answer_text = f"Alignments for {tag} already computed..."
    return responses.JSONResponse(status_code=status, content={"detail": answer_text})



# Model inference API endpoint
@app.get("/openfold_predictions/{model_id}/")
async def infer(model_id, tag: Optional[str] = default_tag, seq: Optional[str] = default_seq):
    tag = tag
    seq = seq
    status=200
    if model_id in models.keys():

        model = models[model_id]

        tmp_fasta_path = os.path.join(output_dir_base, f"tmp_{os.getpid()}.fasta")
        with open(tmp_fasta_path, "w") as fp:
            fp.write(f">{tag}\n{seq}")

        output_name = f'{tag}_{config_preset}'

        local_alignment_dir = os.path.join(alignment_dir, tag)
        feature_dict = data_processor.process_fasta(
            fasta_path=tmp_fasta_path, alignment_dir=local_alignment_dir)
        # Remove temporary FASTA file
        #os.remove(tmp_fasta_path)

        processed_feature_dict = feature_processor.process_features(
            feature_dict, mode='predict')

        processed_feature_dict = {
                k:torch.as_tensor(v, device=device)
                for k,v in processed_feature_dict.items()
            }

        batch = processed_feature_dict.copy()

        with torch.no_grad():
            # Temporarily disable templates if there aren't any in the batch
            template_enabled = model.config.template.enabled
            model.config.template.enabled = template_enabled and any([
                "template_" in k for k in batch
            ])

            logger.info(f"Running inference for {tag}...")
            t = time.perf_counter()
            out = model(batch)
            inference_time = time.perf_counter() - t
            logger.info(f"Inference time: {inference_time}")

            model.config.template.enabled = template_enabled

        # Toss out the recycling dimensions --- we don't need them anymore
        processed_feature_dict = tensor_tree_map(
            lambda x: np.array(x[..., -1].cpu()),
            processed_feature_dict
        )
        out = tensor_tree_map(lambda x: np.array(x.cpu()), out)

        unrelaxed_protein = prep_output(
                out,
                processed_feature_dict,
                feature_dict,
                feature_processor
            )

        output_directory = os.path.join(output_dir_base, "predictions")
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        unrelaxed_output_path = os.path.join(
                output_directory, f'{output_name}_unrelaxed.pdb'
            )

        with open(unrelaxed_output_path, 'w') as fp:
                fp.write(protein.to_pdb(unrelaxed_protein))

        logger.info(f"Output written to {unrelaxed_output_path}...")

        #Upload output dir to S3
        answer_text = f"Output for {model_id} uploaded to S3"

    else:
        status=404
        answer_text = f"Model {model_id} does not exist. Try a model name up to model{num_models-1}"
        logger.warning(answer_text)
    return responses.JSONResponse(status_code=status, content={"detail": answer_text})



# Load Traced Models
# Load models in memory and onto accelerator as needed

ckpt_path = '/fsx-shared/openfold/openfold_params/'+ model_name+ '.pt'

logger.warning(f"Loading {num_models} instances of pre-trained model {model_name} from path {ckpt_path} ...")

for i in range(num_models):
    model_id = 'model_' + str(i)
    logger.warning(f"   {model_id} ...")

    one_model = AlphaFold(config)
    one_model = one_model.eval()
    d = torch.load(ckpt_path)

    if "ema" in d:
        # The public weights have had this done to them already
        d = d["ema"]["params"]
    one_model.load_state_dict(d)

    models[model_id] = one_model
    if device_type=='gpu':
        model=models[model_id]
        model.to(device)
        logger.info(
                f"Loaded OpenFold parameters for {model_name}..."
            )
    elif device_type=='inf':
        logger.warning("INF not supported yet....")

