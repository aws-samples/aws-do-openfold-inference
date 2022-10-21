import requests
from urllib.parse import urlparse
import socket

tag = 'seq0'
seq = 'MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH'

session = requests.Session()

#get_alignment_url = "http://openfold-gpu-0.default.svc.cluster.local:8080/openfold_predictions/model_0?tag="+tag+"&seq="+seq
get_alignment_url = "http://localhost:8081/openfold_predictions/model_0/"
urlparts = urlparse(get_alignment_url)
hostname = urlparts.hostname
hostip = socket.gethostbyname(hostname)
port = ''
if urlparts.port != None:
    port = f":{urlparts.port}"
pred_replace = f"{urlparts.scheme}://{hostip}{port}{urlparts.path}"
result = session.get(pred_replace)
