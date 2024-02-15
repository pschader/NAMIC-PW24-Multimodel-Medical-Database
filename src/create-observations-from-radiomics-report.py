#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import glob
import requests
from fhir.resources.observation import Observation


def parse_radiomics_results(path):
    tree = ET.parse(path)
    root = tree.getroot()
    namespaces = {'mp': 'http://www.mitk.org/Phenotyping'}

    data = {}
    measurement_method = root.find('mp:measurementMethod', namespaces)
    if measurement_method is not None:
        data["method"] = measurement_method.find('mp:name', namespaces).text
        data["organisation"] = measurement_method.find('mp:organisation', namespaces).text
        data["method_version"] = measurement_method.find('mp:version', namespaces).text

    image = root.find('mp:image', namespaces)
    if image is not None:
        data["seriesInstanceUID"] = image.find('mp:seriesInstanceUID', namespaces).text
        data["imageFilePath"] = image.find('mp:filePath', namespaces).text

    mask = root.find('mp:mask', namespaces)
    if mask is not None:
        data["maskFilePath"] = mask.find('mp:filePath', namespaces).text
        data["label"] = data["maskFilePath"].split('/')[-1].split('--')[-1].split('.')[0]
        data["segmentationSeriesUID"] = data["maskFilePath"].split('/')[-1].split('--')[0] 

    features = root.findall('mp:features/mp:feature', namespaces)
    data["features"] = {}
    for feature in features:
        data["features"][feature.get('name')] = feature.text
    return data

# Open Points:
# - Reference Patient
# - Refrence Segmentation
# - How to represent Segmentation? One ImagingSelection per segmentation

def create_observations(data):
    for feature in data["features"]:
        yield Observation(**{
            "status": "final",
            "code": {
                "coding": [ {
                    "system": "http://www.mitk.org/Phenotyping",
                    "code": feature,
                    "display": feature,
                }]
            },
            "valueQuantity": {
                "value": data["features"][feature],
            },
           #"derivedFrom": [{
           #    "identifier": {
           #        value: "", #f"urn:oid:{data['segmentationSeriesUID']}",
           #    },
           #    "type": "ImagingSelection"
           #}]
        })

xml_results = glob.glob('radiomics/data/**/*radiomics.xml', recursive=True)


data = []
for result in xml_results:
    data.append(parse_radiomics_results(result))

observations = []
for d in data:
    observations.extend(create_observations(d))

# print(f"Created {len(observations)} observations")
# print(observations[0].json())

# print("Post Observations to FHIR Server")
# fhir_session = requests.Session()
# for observation in observations:
#   r = fhir_session.post("http://localhost:8080/fhir/Observation", json=observation.json())
#   r.raise_for_status()

filepath='data/fhir-resources/radiomics-observations.json'
print(f"Writing {filepath}")
with open(filepath, 'w') as fp:
    for observation in observations:
        fp.write(observation.json())
