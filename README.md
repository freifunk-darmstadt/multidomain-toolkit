# Multidomain Toolkit

Create Polygons on Google's My Maps, convert them to GeoJSON and use that to assign Freifunk nodes from a `meshviewer.json` compatible URL to domains.

## Requirements

- python3
- pipenv
    - `pip install --upgrade pipenv`

## Preparation

Clone the repository and install necessary dependencies

```shell
git clone https://github.com/freifunk-darmstadt/multidomain-toolkit.git
cd multidomain-toolkit/
pipenv install
pipenv shell
```

## Workflow

1. Create Polygons matching your desired domains on [Google My Maps](https://www.google.com/mymaps)
2. Use the `Export to KML``option to export your polygons in KML format
3. Call `./kml2geojson.py ` to convert the KML export to GeoJSON
4. Call `./nodedistribution.py` to assign nodes to domain polygons
