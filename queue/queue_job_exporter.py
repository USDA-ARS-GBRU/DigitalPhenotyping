import redis
from dotenv import dotenv_values
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


opts = {
    "connection": {
        "host": config['REDIS_HOST'],
        'port': config['REDIS_PORT'],
        'username': config['REDIS_USER'],
        'password': config['REDIS_PASSWORD']
    },
}

queue = bullQueue(config['REDIS_QUEUE'], opts=opts)
async def run():
    jobs = await queue.getJobs(['wait'])
    out = {}
    for job in jobs:
        out[job.name] = job.data
    with open("tmp/citrus_hfl_data.json", "w") as f:
        json.dump(out, f)
    await queue.close()
asyncio.run(run())
# # config = dotenv_values(".env.demo_breedbase")
# config = dotenv_values(".env.citrus_breedbase")
# FIELD_ID = 290


# # Connect to the Redis database
# r = redis.Redis(host=config['REDIS_HOST'], port=config['REDIS_PORT'],
#                 db=0, username=config['REDIS_USER'], password=config['REDIS_PASSWORD'])

# # Get all the keys in the database
# keys = r.keys()
# print(keys)

# print(r.get(str(keys[0])))

# Open a file to write the data to
# with open('tmp/redis_keys_export.rdb', 'wb') as f:
#     # str_keys = str(keys)
#     # f.write(bytes(str_keys, encoding="utf8"))
#     for key in keys:
#         f.write(key)
#         f.write(b"\n")

# Open a file to write the data to
# with open('tmp/redis_export.rdb', 'wb') as f:
#     # Iterate over the keys and dump the data to the file
#     out = []
#     for key in keys:
#         data = r.dump(key)
#         data = r.get(key)
#         out.append(data)
#     f.writelines(out)

