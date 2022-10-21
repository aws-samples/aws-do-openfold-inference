import re
import os

def parse_fasta(data):
    data = re.sub('>$', '', data, flags=re.M)
    lines = [
        l.replace('\n', '')
        for prot in data.split('>') for l in prot.strip().split('\n', 1)
    ][1:]
    tags, seqs = lines[::2], lines[1::2]

    tags = [t.split()[0]+'_'+t.split()[6] for t in tags]

    return tags, seqs

cameo_path = '/fsx-shared/openfold/cameo/'

test_squences_path = cameo_path + '/cameo_protein_targets.fasta'

# Gather input sequences
with open(test_squences_path, "r") as fp:
    data = fp.read()

tags, seqs = parse_fasta(data)

if not os.path.isdir(cameo_path+"/cameo-fastas"):
    os.mkdir(cameo_path+"/cameo-fastas")

for tag, seq in zip(tags, seqs):
    tmp_fasta_path = os.path.join(cameo_path , 'cameo-fastas', f"tmp_{tag}.fasta")
    with open(tmp_fasta_path, "w") as fp:
        fp.write(f">{tag}\n{seq}")

