"""mk_status.py lang batch tts_sess/gen mp3date mp3sig stt_sess/gen wdate wsig -> build/st/<lang>_<batch>.json"""
import json,sys
from pathlib import Path
G="https://storage.googleapis.com/xi-backend/database/workspace/11f53bd69c014f2783acf69010a936f3/content_generation/"
Q="?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=xi-backend-prod%40xi-labs.iam.gserviceaccount.com%2F20261029%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date="
l,b,m,md,ms,w,wd,ws=sys.argv[1:9]
gid=w.split("/")[1]
mu=G+m+"/content.mp3"+Q+md+"&X-Goog-Expires=7200&X-Goog-SignedHeaders=host&X-Goog-Signature="+ms
wu=G+w+"/words.json"+Q+wd+"&X-Goog-Expires=7200&X-Goog-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3D%22transcript-"+gid+"-words.json%22&X-Goog-Signature="+ws
p=Path(__file__).resolve().parent.parent/"build"/"st"/f"{l}_{b}.json"
p.write_text(json.dumps({"all_completed":True,"has_failures":False,"transcripts":[{"source":{"url":mu},"words_url":wu}]}))
print(p)
