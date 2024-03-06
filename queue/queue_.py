from bullmq import Queue as bullQueue
import asyncio
import requests
import json
import base64
import os
from zipfile import ZipFile
from requests_toolbelt import MultipartEncoder
from dotenv import dotenv_values

config = dotenv_values(".env.demo_breedbase")
# config = dotenv_values(".env.sugarcane_breedbase")


opts = {
    "connection": {
        "host": config['REDIS_HOST'],
        'port': config['REDIS_PORT'],
        'username': config['REDIS_USER'],
        'password': config['REDIS_PASSWORD']
    },
    "defaultJobOptions": {
        "attempts": 3,
        "backoff": {
            "type": 'exponential',
            "delay": 1000,
        }
    }
}

queue = bullQueue(config['REDIS_QUEUE'], opts=opts)
login_url = f"{config['BREEDBASE_URL']}/ajax/user/login?username={config['BREEDBASE_USER']}&password={config['BREEDBASE_PASSWORD']}"
brapi_login_url = f"{config['BREEDBASE_URL']}/brapi/v2/token?username={config['BREEDBASE_USER']}&password={config['BREEDBASE_PASSWORD']}"
brapi_images_url = f"{config['BREEDBASE_URL']}/brapi/v2/images?pageSize=1000"
images_delete_queries = "?object_id={}&action=confirm_delete"
images_delete_url = f"{config['BREEDBASE_URL']}/image/ajax/image_ajax_form.pl"
upload_additional_file_url = f"{config['BREEDBASE_URL']}/ajax/breeders/trial/167/upload_additional_file"


def upload_additional_file(session, tmp_out_dir, rel_file_path):
    m = MultipartEncoder(
        fields={'trial_upload_additional_file': (
            rel_file_path, open(os.path.join(tmp_out_dir, rel_file_path), 'rb'))}
    )
    res = session.post(upload_additional_file_url, data=m, headers={
        'Content-Type': m.content_type})
    file_id = res.json()['file_id']
    return (file_id, f"{config['BREEDBASE_URL']}/breeders/phenotyping/download/{file_id}")


async def main():
    with requests.Session() as s_brapi:
        with requests.Session() as s:
            s.get(login_url)
            res = s_brapi.get(brapi_login_url)
            access_token = res.json().get("access_token")

            with s_brapi.get(brapi_images_url) as res:
                images = res.json()['result']['data']
                for image_data in images:
                    if image_data.get('description'):
                        audio_url = ""
                        print(image_data['imageDbId'], "processing..")
                        print(image_data['description'][:10] if image_data['description'] else image_data.get(
                            'description'))
                        imgDbId = image_data['imageDbId']
                        description = bytes(image_data['description'], 'utf-8')
                        os.makedirs("tmp", exist_ok=True)
                        try:
                            with open("tmp/decode_outfile.zip", 'wb') as f:
                                decoded = base64.b64decode(description)
                                f.write(decoded)
                            with ZipFile("tmp/decode_outfile.zip", 'r') as zObject:
                                zObject.extractall(path=f"tmp/{imgDbId}")
                        except Exception:
                            print(f"{imgDbId} skipping")
                            continue
                        files = os.listdir(f"tmp/{imgDbId}/Output")
                        audio_url = ""
                        log_url = ""
                        trait_url = ""
                        for file in files:
                            if file.endswith(".wav") or file.endswith('mp4') or file.endswith('mp3'):
                                print("Audio", file)
                                audio_file_id, audio_url = upload_additional_file(
                                    s, f"tmp/{imgDbId}/Output", file)

                            if file.endswith('csv'):
                                if "log" in file:
                                    print("Geonav Log", file)
                                    log_file_id, log_url = upload_additional_file(
                                        s, f"tmp/{imgDbId}/Output", file)
                                if "trait" in file:
                                    print("Trait file", file)
                                    trait_file_id, trait_url = upload_additional_file(
                                        s, f"tmp/{imgDbId}/Output", file)
                        job_data = {
                            'audio_url': audio_url,
                            'log_url': log_url,
                            'trait_url': trait_url,
                            'field_id': 167,
                        }
                        await queue.add(f"job_{imgDbId}", job_data, {})
                        print(f"{imgDbId} clearing...")
                        s.get(images_delete_url +
                              images_delete_queries.format(imgDbId))

    # Close when done adding jobs
    await queue.close()

if __name__ == "__main__":
    asyncio.run(main())
