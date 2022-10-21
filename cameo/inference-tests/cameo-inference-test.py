import re
import time
import pandas as pd

import requests
from urllib.parse import urlparse
import socket

def parse_fasta(data):
    data = re.sub('>$', '', data, flags=re.M)
    lines = [
        l.replace('\n', '')
        for prot in data.split('>') for l in prot.strip().split('\n', 1)
    ][1:]
    tags, seqs = lines[::2], lines[1::2]

    tags = [t.split()[0]+'_'+t.split()[6] for t in tags]

    return tags, seqs


test_squences_path = '/fsx-shared/openfold/cameo/cameo_protein_targets.fasta'

# Gather input sequences
with open(test_squences_path, "r") as fp:
    data = fp.read()

tags, seqs = parse_fasta(data)

session = requests.Session()

time_taken_list = []
seq_len_list = []
for tag, seq in zip(tags, seqs):
    # When calling from another instance in cluster
    print(tag)
    get_alignment_url = "http://openfold-gpu-0.default.svc.cluster.local:8080/openfold_predictions/model_0/?tag="+tag+"&seq="+seq
    
    urlparts = urlparse(get_alignment_url)
    hostname = urlparts.hostname
    hostip = socket.gethostbyname(hostname)
    port = ''
    if urlparts.port != None:
        port = f":{urlparts.port}"
    pred_replace = f"{urlparts.scheme}://{hostip}{port}{urlparts.path}?{urlparts.query}"
    #print(pred_replace)
    start_time = time.time()
    result = session.get(pred_replace)
    end_time = time.time()

    time_taken_list.append( end_time - start_time)
    seq_len_list.append(len(seq))

cameo_inference_time_df = pd.DataFrame({'tags':tags, 'inference_time':time_taken_list, 'sequence_length':seq_len_list})

cameo_inference_time_df.to_csv('/fsx-shared/openfold/cameo/inference_output/cameo_inference_time_df.csv')

