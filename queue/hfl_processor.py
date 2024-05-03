import os
import json
from transcribe import transcribe
from phenotype import link_plants

VALID_JOBS = [
              'job_2428',
              'job_2432',
              'job_2433',
              'job_2435',
              'job_2436',
              'job_2439',
              'job_2440',
              'job_2441',
              ]
# 0	miss
# 1	detected but wrong
# 2	correct
# 3	other

TMP_DIR = "tmp"
DO_TRANSCRIBE = False

for job in VALID_JOBS:
    print(job, "processing...")
    job_dir = os.path.join(TMP_DIR, job, "worker")
    for file in os.listdir(job_dir):
        # print(file)
        if file.strip().endswith(".mp4"):
            audio_file = os.path.join(job_dir, file)
        if file.strip().endswith(".csv"):
            if "log" in file:
                log_file = os.path.join(job_dir, file)
    
    if DO_TRANSCRIBE:
        transcript = transcribe(audio_file, job_dir)
        print(transcript['text'])
    else: 
        with open(audio_file+"_transcript.json", "r") as f:
            transcript = json.load(f)

    # plant_features = link_plants(
    #     transcript, log_file, trait_file=None, type="timestamp_with_log", TMP_DIR=job_dir, audio_file=audio_file)
    plant_features = link_plants(
        transcript['text'], log_file, trait_file=None, type="transcript", TMP_DIR=job_dir)
    print(plant_features)
    # break
