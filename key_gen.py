import json
from typing import Dict

import requests

result = requests.get(
    "https://code.highcharts.com/mapdata/countries/in/in-all.topo.json"
)

geo_json: Dict = result.json()
final: Dict = {}

for geo in geo_json["objects"]["default"]["geometries"]:
    hc_key = geo["properties"]["hc-key"]
    name = geo["properties"]["name"]
    final[name] = hc_key

value = json.dumps(final, indent=2)

with open("key_mapper.json", "w") as file:
    file.write(value)
