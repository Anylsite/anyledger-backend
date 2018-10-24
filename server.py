from flask import Flask, request
import sqlite3
import json
import binascii

from raiden_libs import utils
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
app.debug = True
db = sqlite3.connect(':memory:')
try:
    db.execute('SELECT temp FROM Sensors')
except sqlite3.OperationalError:
    print("Creating Table Sensors")
    db.execute('CREATE TABLE Sensors (address text, timestamp integer, temp real, lat real, lon real)')


class Sensor:
    def __init__(self, address: str):
        self.address = address

    def save_data(self, timestamp, temp, lat, lon):
        sql_command = '''INSERT INTO Sensors VALUES ("{}", {}, {}, {}, {})'''.format(
            self.address, timestamp, temp, lat, lon)
        print(sql_command)
        db.execute(sql_command)
        db.commit()

    def get_data_as_json(self):
        cur = db.execute('SELECT * FROM Sensors WHERE address = '.format(self.address))
        cur.fetchall()


def join_custom_fractions(real, fraction):
    return '.'.join([str(real), str(fraction)])


sensors = {}


@app.route("/data", methods=['POST'])
def process_iot_data():
    signature = binascii.unhexlify(request.headers['X-Anyledger-Sig'])  # same as binascii.unhexlify()
    eth_addr = utils.address_from_signature(request.data, signature)

    data = json.loads(request.data.decode())
    temp = join_custom_fractions(data['temperature']['val1'], data['temperature']['val2'])
    lat = join_custom_fractions(data['lat']['val1'], data['lat']['val2'])
    lon = join_custom_fractions(data['lon']['val1'], data['lon']['val2'])

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
