import requests
import re
from multiprocessing import Process
from urllib.parse import urlparse
import socket

def model_server_0(sorted_targets):

    session = requests.Session()

    for (tag, tags), seqs in sorted_targets[0:13]:
        for tag, seq in zip(tags, seqs):

            # When calling from model server instance
            #get_alignment_url = "http://localhost:8081/precompute_alignments/?tag="+tag+"&seq="+seq

            # When calling from another instance in cluster
            get_alignment_url = "http://openfold-gpu-0.default.svc.cluster.local:8080/precompute_alignments/?tag="+tag+"&seq="+seq

            urlparts = urlparse(get_alignment_url)
            hostname = urlparts.hostname
            hostip = socket.gethostbyname(hostname)
            port = ''
            if urlparts.port != None:
                port = f":{urlparts.port}"
            pred_replace = f"{urlparts.scheme}://{hostip}{port}{urlparts.path}"
            print(pred_replace)
            result = session.get(pred_replace)

def model_server_1(sorted_targets):

    session = requests.Session()

    for (tag, tags), seqs in sorted_targets[14:24]:
        for tag, seq in zip(tags, seqs):

            # When calling from model server instance
            #get_alignment_url = "http://localhost:8081/precompute_alignments/?tag="+tag+"&seq="+seq

            # When calling from another instance in cluster
            get_alignment_url = "http://openfold-gpu-1.default.svc.cluster.local:8080/precompute_alignments/?tag="+tag+"&seq="+seq

            urlparts = urlparse(get_alignment_url)
            hostname = urlparts.hostname
            hostip = socket.gethostbyname(hostname)
            port = ''
            if urlparts.port != None:
                port = f":{urlparts.port}"
            pred_replace = f"{urlparts.scheme}://{hostip}{port}{urlparts.path}"
            print(pred_replace)
            result = session.get(pred_replace)
    
def parse_fasta(data):
    data = re.sub('>$', '', data, flags=re.M)
    lines = [
        l.replace('\n', '')
        for prot in data.split('>') for l in prot.strip().split('\n', 1)
    ][1:]
    tags, seqs = lines[::2], lines[1::2]

    tags = [t.split()[0] for t in tags]

    return tags, seqs        



if __name__ == '__main__':

    test_squences_path = './test-sequences.fasta'

    # Gather input sequences
    with open(test_squences_path, "r") as fp:
        data = fp.read()

    tag_list = []
    seq_list = []

    tags, seqs = parse_fasta(data)
    # assert len(tags) == len(set(tags)), "All FASTA tags must be unique"
    tag = '-'.join(tags)

    tag_list.append((tag, tags))
    seq_list.append(seqs)

    seq_sort_fn = lambda target: sum([len(s) for s in target[1]])
    sorted_targets = sorted(zip(tag_list, seq_list), key=seq_sort_fn)

    p1 = Process(target=model_server_0)
    p1.start()
    p2 = Process(target=model_server_1)
    p2.start()
    p1.join()
    p2.join()


