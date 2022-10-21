from json import load
import os, subprocess, logging, yaml

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq
import re

ryaml = YAML()
ryaml.preserve_quotes = True

logging.getLogger().setLevel(logging.INFO)


CAMEO_CONFIG = './run-cameo.yaml'

with open(CAMEO_CONFIG) as file:
    cameo_config = ryaml.load(file)


if not os.path.isdir("./cameo-yamls"):
    os.mkdir("./cameo-yamls")

def parse_fasta(data):
    data = re.sub('>$', '', data, flags=re.M)
    lines = [
        l.replace('\n', '')
        for prot in data.split('>') for l in prot.strip().split('\n', 1)
    ][1:]
    tags, seqs = lines[::2], lines[1::2]

    tags = [t.split()[0]+'_'+t.split()[6] for t in tags]

    return tags, seqs
    

test_squences_path = './cameo_protein_targets.fasta'

# Gather input sequences
with open(test_squences_path, "r") as fp:
    data = fp.read()

tags, seqs = parse_fasta(data)

c = 0
for tag, seq in zip(tags, seqs):
    
    #if len(seq) < 700:
    if c < 100:
        one_file_path = '/fsx-shared/openfold/cameo/cameo-fastas/tmp_'+tag+'.fasta'
        cameo_config["metadata"]["name"] = tag.lower().replace('_','-')
        cameo_config["spec"]["containers"][0]['args'][1] = dq('--one_file_path=')+dq(one_file_path)

    

        job_yaml_file = './cameo-yamls/'+tag+'.yaml'
        with open(job_yaml_file, 'w') as file:
            ryaml.dump(cameo_config, file)
    c=c+1





   
#cli_cmd = ['kubectl','apply','-f', job_yaml_file]
#subprocess.run(cli_cmd)
    
    

# we probably don't need this anymore....
# cli_cmd = ['kubectl','apply','-f', TRAIN_CONFIG]
# logging.info(f"Running command: {cli_cmd}")

# TODO: Add the file yaml creation for spawning nodes.



# subprocess.run(cli_cmd)
# subprocess.run(cli_cmd)
# subprocess.run(cli_cmd)
# subprocess.run(cli_cmd)
# subprocess.run(cli_cmd)
