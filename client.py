#!/usr/bin/python3

import iso8601
import sqlite3
import gevent
from gevent.queue import Queue, Empty
import requests
import json
from pprint import pprint

leshan = 'http://localhost:8080/api'
q = Queue()


class LookupTable:
    # {
    # "name": "Energy",
    # "id": 3331,
    # "instancetype": "multiple",
    # "mandatory": false,
    # "description": "This IPSO object should be used to...
    # }

    # to
    # {3331: "Energy"}

    def __init__(self, filename):
        self.table = {}

        with open(filename) as f:
            oma_objectids = json.load(f)
        for o in oma_objectids:
            self.table[o["id"]] = o["name"]

    def lookup(self, i: int) -> str:
        return self.table.get(i, 'Unknown')


class ClientGreenlet(gevent.Greenlet):
    def __init__(self, client_json, server, response_queue, *args, **kwargs):
        self.address = client_json['address']
        self.bindingMode = client_json['bindingMode']
        self.endpoint = client_json['endpoint']
        self.lifetime = client_json['lifetime']
        self.lwM2mVersion = client_json['lwM2mVersion']
        self.queue = response_queue
        # http://localhost:8080/api/ -> http://localhost:8080/api/clients/ilya/3/0/?format=TLV
        self.server_address = '{}/clients/{}'.format(server, self.endpoint)

        self.links = [l['url'] for l in client_json['objectLinks']]

        super().__init__(*args, **kwargs)

    def get(self, url):
        resp = requests.get(self.server_address + url)
        return resp.json()

    def _run(self):
        while True:
            all_endpoints = {}
            for l in self.links:
                all_endpoints[l] = self.get(l)

            timestamp_iso8601 = all_endpoints['/3/0']['content']['resources'][7]['value']
            temp = all_endpoints['/3303/0']['content']['resources'][1]['value']
            lat = all_endpoints['/6/0']['content']['resources'][0]['value']
            lon = all_endpoints['/6/0']['content']['resources'][1]['value']

            # Preprocess data a bit so the Database doesn't have to worry about it
            timestamp = iso8601.parse_date(timestamp_iso8601)

            self.queue.put_nowait((timestamp, temp, lat, lon))
            gevent.sleep(3)


class DatabaseWorker(gevent.Greenlet):
    def __init__(self, response_queue):
        self.q = response_queue

        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        # Hardcoded structure to fit PoC only
        self.c.execute('''CREATE TABLE LeshanMockSensor (timestamp integer, temp real, lat real, lon real)''')

        super().__init__()

    def put(self, timestamp, temp, lat, lon):
        self.c.execute(
            "INSERT INTO LeshanMockSensor VALUES ('{}', '{}', {}, {})".format(timestamp, temp, lat, lon))

    def get(self):
        return self.c.execute('SELECT * FROM LeshanMockSensor').fetchall()

    def commit(self):
        self.conn.commit()

    def _run(self):
        print("Database current state", self.get())
        while True:
            try:
                item = self.q.get_nowait()
                print("DatabaseWorker found item in Queue", item)
                self.put(item[0], item[1], item[2], item[3])
            except Empty:
                print("DatabaseWorker was very productive")
                self.commit()
                pprint(self.get())
                gevent.sleep(5)


def find_clients(url):
    resp = requests.get(leshan + '/clients')
    client_jsons = resp.json()
    pprint(client_jsons)

    clients = [ClientGreenlet(c, leshan, q) for c in client_jsons]
    return clients


clients = find_clients(leshan)
greenlets = clients + [DatabaseWorker(q)]

for g in greenlets:
    g.start()
gevent.joinall(greenlets)
