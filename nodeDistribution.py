#! /usr/bin/env python3

import json
from shapely.geometry import shape, Point
import requests
from pprint import pprint

NODE_URL="https://meshviewer.darmstadt.freifunk.net/data/ffda/meshviewer.json"

def all_nodes():
    r = requests.get(NODE_URL)
    data = json.loads(r.text)
    all_nodes = []
    without_location = []
    for node in data["nodes"]:
        if node.get("location", None):
            lon = node["location"]["longitude"]
            lat = node["location"]["latitude"]

            n = {"node_id": node["node_id"],
                 "name": node["hostname"],
                 "point": Point(lon, lat)}
            all_nodes.append(n)
        else:
            without_location.append(node)

    print("Found {} nodes without location".format(len(without_location)))
    print("Found {} nodes with location".format(len(all_nodes)))

    return all_nodes

def find_domain(point, polygons):
    for domainname, polygon in polygons.items():
        if polygon.contains(point):
            return domainname
    return "unknown"

def main():
    with open('ffda_domains.geojson') as fh:
        data = json.load(fh)

    domains = {}
    polygons =  {}

    # Load all polygons from geojson
    for feature in data['features']:
        p = shape(feature['geometry'])
        domainname = feature["properties"]["name"]
        polygons[domainname] = p

    for node in all_nodes():
        domainname = find_domain(node["point"], polygons)
        if not domains.get(domainname, None):
            domains[domainname] = []
        domains[domainname].append(node["name"])


    for domain, nodes in domains.items():
        print("{: >80} has {: >3} nodes".format(domain, len(nodes)))


if __name__ == "__main__":
    main()
