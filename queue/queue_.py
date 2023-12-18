from bullmq import Queue as bullQueue
import asyncio

opts={"connection": {"host": 'redis-16755.c61.us-east-1-3.ec2.cloud.redislabs.com',
                                                                        'port': 16755,
                                                                        'username': 'tester',
                                                                        'password': 'Mitanshu@12'}}
opts={}
queue = bullQueue("myQueue", opts=opts)


async def main():
    # Add a job with data { "foo": "bar" } to the queue
    for i in range(1):
        pass
        # await queue.add("myJob", {
        #     "audio_url": 'https://demo.breedbase.org/breeders/phenotyping/download/42',
        #     "field_id": 167,
        #     "file_id": 42
        # }, {})

    jobs = await queue.getFailed()
    print(jobs)


    # Close when done adding jobs
    await queue.close()

if __name__ == "__main__":
    asyncio.run(main())
