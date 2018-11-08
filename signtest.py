from coincurve import PublicKey, PrivateKey
from raiden_libs import utils
import binascii
import time
import json

trip_along_ringbahn_raw = [
    {'timestamp': int(time.time()) - 10000, 'lat': {'val1': 52, 'val2': 536131},
     'lon': {'val1': 13, 'val2': 447444}, 'temperature': {"val1": 19, "val2": 0}},
    {'timestamp': int(time.time()) - 9000, 'lat': {'val1': 52, 'val2': 538221},
     'lon': {'val1': 13, 'val2': 44376}, 'temperature': {"val1": 20, "val2": 0}},
    {'timestamp': int(time.time()) - 8000, 'lat': {'val1': 52, 'val2': 540247},
     'lon': {'val1': 13, 'val2': 43899}, 'temperature': {"val1": 21, "val2": 0}},
    {'timestamp': int(time.time()) - 7000, 'lat': {'val1': 52, 'val2': 541751},
     'lon': {'val1': 13, 'val2': 43513}, 'temperature': {"val1": 22, "val2": 0}},
    {'timestamp': int(time.time()) - 6000, 'lat': {'val1': 52, 'val2': 54264},
     'lon': {'val1': 13, 'val2': 433692}, 'temperature': {"val1": 23, "val2": 0}},
    {'timestamp': int(time.time()) - 5000, 'lat': {'val1': 52, 'val2': 543007},
     'lon': {'val1': 13, 'val2': 431339}, 'temperature': {"val1": 24, "val2": 0}},
    {'timestamp': int(time.time()) - 4000, 'lat': {'val1': 52, 'val2': 543755},
     'lon': {'val1': 13, 'val2': 428731}, 'temperature': {"val1": 25, "val2": 0}},
    {'timestamp': int(time.time()) - 3000, 'lat': {'val1': 52, 'val2': 544295},
     'lon': {'val1': 13, 'val2': 427207}, 'temperature': {"val1": 27, "val2": 0}},
]

private_key = PrivateKey()
trip_along_ringbahn = []
for t in trip_along_ringbahn_raw:
    t_json = json.dumps(t)
    signature = utils.sign(private_key, t_json.encode()).hex().upper()
    trip_along_ringbahn.append((t_json, signature))
    print('curl http://localhost:5000/data -X POST --header "X-Anyledger-Sig: {}" --header "Content-Type: application/json" -d \'{}\''.format(signature, t_json))

