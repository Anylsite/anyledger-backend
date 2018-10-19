from flask import Flask
from flask import request
from coincurve import PublicKey
from eth_utils import decode_hex, keccak
import hashlib
import json

from gevent.pywsgi import WSGIServer
import ipdb

app = Flask(__name__)
app.debug = True


class Sensor:
    def __init__(self):
        self.data = []

    def log(self, timestamp, temp, lat, lon):
        self.data.append((timestamp, temp, lat, lon))


def join_custom_fractions(real, fraction):
    return '.'.join([str(real), str(fraction)])


def convert_eth_signature(signature: bytes):
    # Support Ethereum's EC v value of 27 and EIP 155 values of > 35.
    if signature[-1] >= 35:
        network_id = (signature[-1] - 35) // 2
        signature = signature[:-1] + bytes([signature[-1] - 35 - 2 * network_id])
    elif signature[-1] >= 27:
        signature = signature[:-1] + bytes([signature[-1] - 27])
    return signature


def public_key_from_signature(data: bytes, signature: bytes, hasher=keccak):
    """Convert an EC signature into a public key."""
    if not isinstance(signature, bytes) or len(signature) != 65:
        raise Exception('Invalid signature, must be 65 bytes')

    signature = convert_eth_signature(signature)

    try:
        signer_pubkey = PublicKey.from_signature_and_message(signature, data, hasher=hasher)
        return signer_pubkey
    except Exception as e:  # pylint: disable=broad-except
        # coincurve raises bare exception on verify error
        raise Exception('Invalid signature')


def eth_sign_sha3(data: bytes) -> bytes:
    """
    eth_sign/recover compatible hasher
    Prefixes data with "\x19Ethereum Signed Message:\n<len(data)>"
    """
    prefix = b'\x19Ethereum Signed Message:\n'
    if not data.startswith(prefix):
        data = prefix + b'%d%s' % (len(data), data)
    return keccak(data)


def prefix(data: bytes) -> bytes:
    """
    Prefixes data with "\x19Ethereum Signed Message:\n<len(data)>"
    """
    prefix = b'\x19Ethereum Signed Message:\n'
    if not data.startswith(prefix):
        data = prefix + b'%d%s' % (len(data), data)
    return data


sensors = {}


@app.route("/data", methods=['POST', 'GET'])
def process_iot_data():
    if request.method == 'POST':
        signature = decode_hex(request.headers['X-Anyledger-Sig'])  # same as binascii.unhexlify()
        pk = public_key_from_signature(prefix(request.data), signature)
        ipdb.set_trace()
        pk.verify(convert_eth_signature(signature), prefix(request.data), hasher=keccak)
        data = json.loads(request.data.decode())
        temp = join_custom_fractions(data['temperature']['val1'], data['temperature']['val2'])
        lat = join_custom_fractions(data['lat']['val1'], data['lat']['val2'])
        lon = join_custom_fractions(data['lon']['val1'], data['lon']['val2'])
        s = sensors.get('default')
        if not s:
            sensors['default'] = s = Sensor()
        s.log(data['timestamp'], temp, lat, lon)
        return "A OK"
    return "You should be using POST to submit some data"


if __name__ == "__main__":
    http = WSGIServer(('', 5000), app)
    http.serve_forever()
