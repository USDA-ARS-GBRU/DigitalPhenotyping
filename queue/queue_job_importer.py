import redis
from dotenv import dotenv_values

config = dotenv_values(".env.demo_breedbase")
# config = dotenv_values(".env.citrus_breedbase")
FIELD_ID = 290


# Connect to the Redis database
r = redis.Redis(host=config['REDIS_HOST'], port=config['REDIS_PORT'],
                db=0, username=config['REDIS_USER'], password=config['REDIS_PASSWORD'])

# Open a file to write the data to
with open('tmp/redis_keys_export.rdb', 'rb') as f:
    byte_str_keys = f.readlines()
    print(byte_str_keys)
    keys = byte_str_keys
    # keys = bytes.decode(byte_str_keys)[1:-1].split(", ")
    keys = [x[:-1] for x in keys]

print(type(keys), len(keys))
print(type(keys[0]))
print(keys)

# Open a file to write the data to
with open('tmp/redis_export.rdb', 'rb') as f:
    # Iterate over the keys and dump the data to the file
    dumps = f.readlines()
    for key, value in zip(keys, dumps):
        r.restore(key, ttl=0, value=value)

# Close the file
f.close()
