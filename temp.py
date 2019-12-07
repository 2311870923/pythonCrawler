import redis
import time
import random

token_arr = [
    'b0036a7a62eda0678a1d4b19f25a4a4f',
    'e215e25777cb917459d48f806f2a3b42',
    'a670c4f234d935d0dd79a0f5245f01c9'
]
r = redis.Redis(host='47.105.174.154', port='6379', password='myangel201314', db=0)

while True:
    token = random.choice(token_arr)
    r.set('token', token)
    time.sleep(3)
