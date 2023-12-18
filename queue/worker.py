from bullmq import Worker
import asyncio
from phenotype_job import process_job
import os


async def process(job, _):
    # job.data will include the data added to the queue
    print(job.data)
    process_job(job.data)


async def main():
    opts={"connection": {"host": 'redis-16755.c61.us-east-1-3.ec2.cloud.redislabs.com',
                                                                        'port': 16755,
                                                                        'username': 'tester',
                                                                        'password': 'Mitanshu@12'}}
    # opts={}
    # Feel free to remove the connection parameter, if your redis runs on localhost
    worker = Worker("myqueue", process, opts=opts)

    while True:
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
