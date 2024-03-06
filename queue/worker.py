from bullmq import Worker
import asyncio
from phenotype_job import process_job
import os
from dotenv import dotenv_values

config = dotenv_values(".env.demo_breedbase")
# config = dotenv_values(".env.sugarcane_breedbase")

async def processor(job, _):
    # job.data will include the data added to the queue
    print(job.data)
    process_job(job.name, job.data)


async def main():
    opts = {"connection": {"host": config['REDIS_HOST'],
                           'port': config['REDIS_PORT'],
                           'username': config['REDIS_USER'],
                           'password': config['REDIS_PASSWORD']}}
    worker = Worker(config['REDIS_QUEUE'], processor, opts=opts)
    worker.close()

    while True:
        break
        await asyncio.sleep(1)
        if worker.drained:
            print("="*10 + "\nAll jobs completed")
            # try:
            #     os.remove("tmp.mp3",)
            # except Exception as e:
            #     print(e)
            await worker.close()
            return

    # When no need to process more jobs we should close the worker

if __name__ == "__main__":
    asyncio.run(main())
