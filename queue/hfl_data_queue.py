from bullmq import Queue as bullQueue
import asyncio
import requests
import json
import base64
import os
from zipfile import ZipFile
from requests_toolbelt import MultipartEncoder
from dotenv import dotenv_values

# config = dotenv_values(".env.demo_breedbase")
config = dotenv_values(".env.citrus_breedbase")
FIELD_ID = 290
hfl_data = "tmp/citrus_hfl_data.json"


opts = {
    "connection": {
        "host": config['REDIS_HOST'],
        'port': config['REDIS_PORT'],
        'username': config['REDIS_USER'],
        'password': config['REDIS_PASSWORD']
    },
}

queue = bullQueue(config['REDIS_QUEUE'], opts=opts)
login_url = f"{config['BREEDBASE_URL']}/ajax/user/login?username={config['BREEDBASE_USER']}&password={config['BREEDBASE_PASSWORD']}"
brapi_login_url = f"{config['BREEDBASE_URL']}/brapi/v2/token?username={config['BREEDBASE_USER']}&password={config['BREEDBASE_PASSWORD']}"
brapi_images_url = f"{config['BREEDBASE_URL']}/brapi/v2/images?pageSize=1000"
images_delete_queries = "?object_id={}&action=confirm_delete"
images_delete_url = f"{config['BREEDBASE_URL']}/image/ajax/image_ajax_form.pl"
upload_additional_file_url = f"{config['BREEDBASE_URL']}/ajax/breeders/trial/{FIELD_ID}/upload_additional_file"


def upload_additional_file(session, tmp_out_dir, rel_file_path):
    m = MultipartEncoder(
        fields={'trial_upload_additional_file': (
            rel_file_path, open(os.path.join(tmp_out_dir, rel_file_path), 'rb'))}
    )
    res = session.post(upload_additional_file_url, data=m, headers={
        'Content-Type': m.content_type})
    file_id = res.json()['file_id']
    return (file_id, f"{config['BREEDBASE_URL']}/breeders/phenotyping/download/{file_id}")


async def processor():
    with requests.Session() as s_brapi:
        with requests.Session() as s:
            s.get(login_url)
            res = s_brapi.get(brapi_login_url)
            access_token = res.json().get("access_token")

            with open(hfl_data) as f:
                hfl_jobs = json.load(f)
            
            # Sample case
            for k,v in hfl_jobs.items():
                await queue.add(k, v, {})


async def main():
    try:
        await processor()
    except Exception as e:
        print(e)
    finally:
        # Close when done adding jobs
        await queue.close()

if __name__ == "__main__":
    asyncio.run(main())
