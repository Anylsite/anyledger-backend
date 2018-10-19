from eth_utils import keccak
from server import prefix, convert_eth_signature, public_key_from_signature
import binascii

signature = binascii.unhexlify(
    'CC9E2B0B338D1BDD1328D88E6750F7CE5F7C6DEA8D73D4DE43E7755029576C1F07D8954640CB698A802729C4C31B17E9D1BF92B23A6CAEEAA2477087D5CCF3541C')
message = prefix(
    b'{"timestamp":4180,"temperature":{"val1":25,"val2":173643},"lat":{"val1":1,"val2":2},"lon":{"val1":-4,"val2":5}}')
pk = public_key_from_signature(message, signature, hasher=keccak)
print(binascii.hexlify(pk.format()))
print("Verifying Message")
pk.verify(convert_eth_signature(signature), message, hasher=keccak)
