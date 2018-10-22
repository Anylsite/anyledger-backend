from collections import namedtuple
from flask import Flask, request
import json
import binascii

from raiden_libs import utils
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
app.debug = True

Datapoint = namedtuple('Datapoint', ['timestamp', 'temp', 'lat', 'lon'])


class Sensor:
    def __init__(self, address: str):
        self.address = address
        self.data = []

    def save_data(self, timestamp, temp, lat, lon):
        self.data.append(Datapoint(timestamp, temp, lat, lon))

    def get_data_as_json(self):
        return json.dumps([d._asdict() for d in self.data])


def join_custom_fractions(real, fraction):
    return '.'.join([str(real), str(fraction)])


eth_smart_contract_mock = {
    '0x416E281ca1B9D5BC93849305d15f1B40F33B599E': True
}
sensors = {}


@app.route("/data", methods=['POST'])
def process_iot_data():
    signature = binascii.unhexlify(request.headers['X-Anyledger-Sig'])  # same as binascii.unhexlify()
    eth_addr = utils.address_from_signature(request.data, signature)

    data = json.loads(request.data.decode())
    temp = join_custom_fractions(data['temperature']['val1'], data['temperature']['val2'])
    lat = join_custom_fractions(data['lat']['val1'], data['lat']['val2'])
    lon = join_custom_fractions(data['lon']['val1'], data['lon']['val2'])

    # Check if IoT device has permissions with our hub.
    if not eth_smart_contract_mock.get(eth_addr, False):
        return "IoT device not authorized", 403

    # If the sensor does not exist yet, create it.
    # Log the data.
    s = sensors.get(eth_addr)
    if not s:
        sensors[eth_addr] = s = Sensor(address=eth_addr)
    s.save_data(data['timestamp'], temp, lat, lon)

    return "Done"


@app.route("/sensors/")
@app.route("/sensors/<eth_addr>", methods=['GET'])
def get_data_for_sensor(eth_addr=None):
    if not eth_addr:
        return json.dumps(list(sensors.keys()))
    sensor = sensors[eth_addr]
    return sensor.get_data_as_json()


if __name__ == "__main__":
    http = WSGIServer(('', 5000), app)
    http.serve_forever()
