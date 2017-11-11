#! /usr/bin/env python3

import json
import logging
from argparse import ArgumentParser
from shapely.geometry import shape, Point
import requests


def all_nodes(url):
    data = requests.get(url).json()
    logging.info("[meshviewer.json] loaded {0}, with {1} nodes and {2} links".format(
        url, len(data.get('nodes', [])), len(data.get('links', []))
    ))

    nodes = []
    nodes_no_location = []
    for node in data["nodes"]:
        if node.get("location", None):
            nodes.append({
                "node_id": node["node_id"],
                "name": node["hostname"],
                "point": Point(
                    node["location"]["longitude"],
                    node["location"]["latitude"]
                )
            })
        else:
            nodes_no_location.append(node)

    logging.info("[meshviewer.json] found {0} nodes with GPS location, {1} without".format(
        len(nodes), len(nodes_no_location)
    ))

    return nodes


def find_domain(node, polygons):
    for domainname, polygon in polygons.items():
        if polygon.contains(node.get('point')):
            logging.debug("[shapely] node {0} ({1}) matches domain {2}".format(
                node['name'], node['node_id'], domainname
            ))
            return domainname
    logging.warning("[shapely] node {0} ({1}) does not match any domain".format(
        node['name'], node['node_id']
    ))
    return "unknown"


def main(geojson_file, meshviewer_json_url):
    domains = {}
    polygons = {}

    # Load all polygons from geojson
    with open(geojson_file) as fh:
        data = json.load(fh)
        logging.debug('[geojson] contains {0} features'.format(
            len(data.get('features', {}))
        ))
    for feature in data['features']:
        polygon = shape(feature['geometry'])
        domainname = feature["properties"]["name"]
        polygons[domainname] = polygon
        logging.debug('[geojson] found feature {0}: {1} '.format(
            domainname, polygon
        ))

    # Match nodes against domain polygons
    for node in all_nodes(meshviewer_json_url):
        domainname = find_domain(node, polygons)
        if not domains.get(domainname, None):
            domains[domainname] = []
        domains[domainname].append(node["name"])

    for domain, nodes in domains.items():
        print("{: >80} has {: >3} nodes".format(domain, len(nodes)))


if __name__ == '__main__':
    argparser = ArgumentParser()

    argparser.add_argument(
        '-v', action='store_true', dest='verbose',
        help='Verbose logging'
    )
    argparser.add_argument(
        '-d', action='store_true', dest='debug',
        help='Debug logging'
    )

    argparser.add_argument(
        '-b', dest='geojson_file',
        help='GeoJSON compatible file containing polygons defining boundaries'
    )
    argparser.add_argument(
        '-m', dest='meshviewer_json_url', required=True,
        help='HTTP URL to a meshviewer.json compatible file',
        default='https://meshviewer.darmstadt.freifunk.net/data/ffda/meshviewer.json'
    )

    args = argparser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    main(args.geojson_file, args.meshviewer_json_url)
