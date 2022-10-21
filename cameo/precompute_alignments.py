import re
import os
from openfold.data import data_pipeline
import argparse
#from openfold.utils.tensor_utils import (
#    tensor_tree_map,
#)

def precompute_alignments(alignment_dir,no_cpus,tmp_fasta_path):
    with open(tmp_fasta_path, "r") as fp:
        data = fp.read()
    lines = [l.replace('\n', '')for prot in data.split('>') for l in prot.strip().split('\n', 1)][1:]
    tags, seqs = lines[::2], lines[1::2]
    tag = tags[0]

    local_alignment_dir = os.path.join(alignment_dir, tag)
    if not os.path.exists(local_alignment_dir):
        os.makedirs(local_alignment_dir, exist_ok=True)

        alignment_runner = data_pipeline.AlignmentRunner(
                jackhmmer_binary_path='/usr/bin/jackhmmer',
                hhblits_binary_path='/usr/bin/hhblits',
                hhsearch_binary_path='/usr/bin/hhsearch',
                uniref90_database_path='/fsx-shared/openfold/data/uniref90/uniref90.fasta',
                mgnify_database_path='/fsx-shared/openfold/data/mgnify/mgy_clusters_2018_12.fa',
                bfd_database_path='/fsx-shared/openfold/data/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt',
                uniclust30_database_path='/fsx-shared/openfold/data/uniclust30/uniclust30_2018_08/uniclust30_2018_08',
                pdb70_database_path='/fsx-shared/openfold/data/pdb70/pdb70',
                no_cpus=no_cpus
            )
        alignment_runner.run(tmp_fasta_path, local_alignment_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cpus", type=int, default=4,
        help="""Number of CPUs with which to run alignment tools"""
    )

    parser.add_argument(
        "--one_file_path", type=str,
        help="""Path to one fast file"""
    )
    
    args = parser.parse_args()
    alignment_dir = '/fsx-shared/openfold/cameo'
    precompute_alignments(alignment_dir,no_cpus = args.cpus, tmp_fasta_path = args.one_file_path)


