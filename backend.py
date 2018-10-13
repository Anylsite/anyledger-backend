#!/usr/bin/python3

import requests
from pprint import pprint


class Client:
    def __init__(self, client_json):
        self.address = client_json['address']
        self.bindingMode = client_json['bindingMode']
        self.endpoint = client_json['endpoint']
        self.lastUpdate = client_json['lastUpdate']
        self.lifetime = client_json['lifetime']
        self.lwM2mVersion = client_json['lwM2mVersion']

        self.links = [l['url'] for l in client_json['objectLinks']]

    def __repr__(self):
        return '< {} {}@{} >'.format(self.__class__, self.endpoint, self.address)


leshan = 'http://localhost:8080/api'


def find_clients(url):
    resp = requests.get(leshan + '/clients')
    client_jsons = resp.json()
    pprint(client_jsons)

    clients = [Client(c) for c in client_jsons]
    return clients


clients = find_clients(leshan)

print(clients)
print(clients[0].links)
