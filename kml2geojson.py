#! /usr/bin/env python3

import logging
from argparse import ArgumentParser

import geojson
from fastkml import kml
from geojson import Feature, Polygon, FeatureCollection


def main(kml_file, outfile):
    # Load KML Data from file
    k = kml.KML()
    with open(kml_file) as fh:
        k.from_string(fh.read().encode())

    # Get list of domains out of KML document
    document = list(k.features()).pop()
    areas = list(document.features())

    # Iterate over kml areas and create geojson features for every area
    feature_list = []
    for area in areas:
        geojson_coords = [
            (p[0], p[1]) for p in list(area.geometry.exterior.coords)
        ]
        feature = Feature(
            geometry=Polygon([geojson_coords]),
            properties={"name": area.name}
        )
        feature_list.append(feature)
        logging.debug(
            'area "{0}" is a polygon consisting of {1} points'.format(
                area.name, len(area.geometry.exterior.coords)
        ))

    # FeatureCollection for all Domains
    features = FeatureCollection(feature_list)
    logging.info('Converted {0} features from KML to GeoJSON'.format(
        len(feature_list)))

    # Check for errors in GeoJSON
    errors = features.errors()

    if len(errors) == 0:
        # Export GeoJson to file if there are no erors
        with open(outfile, 'w') as fh:
            fh.write(geojson.dumps(features))
        logging.info('Wrote GeoJSON to {0}'.format(outfile))
    else:
        logging.error('GeoJSON data contains errors, aborting')
        logging.error(errors)


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
        '-k', dest='kml_file', required=True,
        help='KML file that holds the boundary polygons'
    )
    argparser.add_argument(
        '-o', dest='outfile', default='domains.geojson',
        help='Output file to write GeoJSON data into',
    )

    args = argparser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    main(args.kml_file, args.outfile)