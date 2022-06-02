from datetime import datetime
from hashlib import sha256
from random import randint

timestamp = int(datetime.now().timestamp())
timestamp += 10
powcost = 0
nonce = randint(0, 9999999)
counter = 0
while powcost < 4:
    counter += 1
    hashcash = f"{timestamp:010}-{nonce:010}-{counter:010}"
    hashed = sha256(hashcash.encode(encoding='ASCII')).hexdigest()
    powcost = len(hashed) - len(hashed.lstrip('0'))
print(hashcash)
