#!/usr/bin/python3

from time import sleep
import threading
import requests
import json
from pprint import pprint

leshan = 'http://localhost:8080/api'


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


class Client(threading.Thread):
    def __init__(self, client_json, server, *args, **kwargs):
        self.address = client_json['address']
        self.bindingMode = client_json['bindingMode']
        self.endpoint = client_json['endpoint']
        self.lastUpdate = client_json['lastUpdate']
        self.lifetime = client_json['lifetime']
        self.lwM2mVersion = client_json['lwM2mVersion']

        # http://localhost:8080/api/ -> http://localhost:8080/api/clients/ilya/3/0/?format=TLV
        self.server_address = '{}/clients/{}'.format(server, self.endpoint)

        self.links = [l['url'] for l in client_json['objectLinks']]

        super().__init__(*args, **kwargs)

    def get(self, url):
        resp = requests.get(self.server_address + url)
        return resp.json()

    def run(self):
        while True:
            for l in self.links:
                resp = self.get(l)
                pprint(resp)
            print("================================")
            sleep(3)


def find_clients(url):
    resp = requests.get(leshan + '/clients')
    client_jsons = resp.json()
    pprint(client_jsons)

    clients = [Client(c, leshan) for c in client_jsons]
    return clients


clients = find_clients(leshan)

for c in clients:
    c.run()
