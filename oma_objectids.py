import json


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
