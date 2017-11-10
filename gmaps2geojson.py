#! /usr/bin/env python3

from fastkml import kml
from pprint import pprint
from geojson import Feature, Polygon, FeatureCollection, dumps

with open("Domänen.kml") as fh:
    data = fh.read()

# Load KML Data from file
k = kml.KML()
k.from_string(data.encode())

# Get list of domains out of KML document
document = list(k.features()).pop()
domains = list(document.features())

# Iterate over kml domains and create geojson features for every domain
feature_list = []
for zone in domains:
    zone_name = zone.name
    zone_coords = zone.geometry.exterior.coords
    # print("'{}' has a polygon of {} lines".format(zone_name, len(zone_coords)))
    geojson_coords = [(p[0], p[1]) for p in list(zone_coords)]
    polygon = Polygon([geojson_coords])
    feature = Feature(geometry=polygon, properties={"name": zone_name})
    feature_list.append(feature)


# FeatureCollection for all Domains
ffda_domains = FeatureCollection(feature_list)

# Check for errors in GeoJSON
errors = ffda_domains.errors()

if len(errors) == 0:
    # Export GeoJson to file if there are no erors
    with open("domains.geojson", "w") as fh:
        fh.write(dumps(ffda_domains))
    print("Succesfully converted to geojson and saved to 'domains.geojson'")
else:
    print("Won't save domains, because the GeoJSON data contains errors!")
    print(errors)
