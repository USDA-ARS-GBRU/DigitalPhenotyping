# Digital Phenotyping

## Getting started

- Create a local Redis server using the following command or [setup a Redis cloud instance](https://redis.io/docs/latest/operate/rc/databases/create-database/create-essentials-database/).
```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```
- Setup Credentials in the `.env` file. Find format in `.env.sample` file.
- Change directory to be in this folder. 
```
cd digital-phenotyping
```
- Install dependancies
```
pip install -r requirements.txt
```
- Create Redis jobs from exported data
```
python create_jobs.py
```
- Process extracted data to create and upload phenotype files.
```
python worker.py
```

### Creating jobs (THIS IS A WORK-AROUND. FIX WHEN BrAPI SPECIFICATION GETS UPDATED)

This will take the exported files from Fieldbook stored in `/images` section of Breedbase. This is a work around due to BrAPI specification limitations. It will try to sync files every 30 minutes. 

```
python create_jobs.py
```

This script does not shut down on its own, Press `Ctrl/Cmd+C` to stop the script after the processor is asleep.

Description:
- The current pipeline **does not receive** Trial number (Field id) where the files will be stored, so you will have to manually add FIELD_ID in the `create_jobs` file.
- It goes through all images and attempts to find the base64 encoded file in `description` field.
- If the decoded file from the `description` field is a zip file. It outputs the extracted zip into `tmp/{imgID}` folder else it goes to the next image file.
- It then uploads all audio, log and trait files to Breebase trial additional files section.
- It creates a Redis job containing the URIs for all files in the database.

### Processing jobs

This uses the jobs created in the previous step to process the files and store results in the Breebase instance. All intermediate files are stored in `tmp/{jobID}/worker` folder. 

The scripts does not read the trait files for dynamic extraction and exporting. Please update the reference trait variables.

- Update `gemma_feature_prompt.txt`.
- Update `gemma_prompt_instructions.txt`.
- Update Trait List link in `job_processor.py`>`list_url`.

```
python worker.py
```

Description:
- Audio and Geonav log files are downloaded in the worker folder.
- Trancriptions are created in whisper-timestamp format.
- Extraction of features is performed.
- Linking of plants/subplots to their features is performed. (The Linking is currently based on special phrase `new plant`. NEEDS Fixing on timestamp linking)
- Phenotype spreadsheet is created and uploaded to Breedbase. (BrAPI uploading is failing. Using Spreadsheet uploading instead.)