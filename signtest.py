from eth_utils import decode_hex, keccak
from server import prefix, convert_eth_signature_and_data
import binascii

from coincurve import PublicKey, PrivateKey
signature_jozef_orig = decode_hex(
    'CC9E2B0B338D1BDD1328D88E6750F7CE5F7C6DEA8D73D4DE43E7755029576C1F07D8954640CB698A802729C4C31B17E9D1BF92B23A6CAEEAA2477087D5CCF3541C')
message = b'{"timestamp":4180,"temperature":{"val1":25,"val2":173643},"lat":{"val1":1,"val2":2},"lon":{"val1":-4,"val2":5}}'

private_key = PrivateKey()
public_key = private_key.public_key
private_key_2 = PrivateKey()
public_key_2 = private_key.public_key

# Prepare data! Message needs to be prefixed. Signature needs to be EIP converted?
signature_jozef, message = convert_eth_signature_and_data(signature_jozef_orig, message)

signature = private_key.sign_recoverable(prefix(message), hasher=keccak)
print(signature.hex())

public_key_recovered = PublicKey.from_signature_and_message(signature, prefix(message), hasher=keccak)

# Apparently verify() is never used because it doesn't do the signature schema!
