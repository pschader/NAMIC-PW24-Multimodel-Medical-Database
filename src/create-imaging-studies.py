import requests

from pydicom.dataset import Dataset
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from fhir.resources.imagingselection import ImagingSelection

session = requests.Session()
session.auth = HTTPBasicAuth('admin', 'admin')
session.headers = {
  'Accept': 'application/dicom+json'
}

BASE_URL = 'http://localhost:8042/dicom-web'

def request(endpoint: str):
  response = session.get(BASE_URL+endpoint)
  response.raise_for_status()

  objects = []
  for x in response.json():
    objects.append(Dataset.from_json(x))
  return objects

print("Find segmentation instances...")
seg_instances_metadata = request('/instances?00080060=SEG')

print("Fetch segmentation instances metadata")
seg_instances = []
for seg_instance_metadata in tqdm(seg_instances_metadata):
  seg_instances.extend(request(f'/studies/{seg_instance_metadata.StudyInstanceUID}/series/{seg_instance_metadata.SeriesInstanceUID}/instances/{seg_instance_metadata.SOPInstanceUID}/metadata'))

print(f"Found {len(seg_instances)} segmentation instances")

def create_imaging_selections(seg_instances):
  for seg_instance in seg_instances:
    for segment in seg_instance.SegmentSequence:
      # TODO
      # - Subject
      imaging_selection = ImagingSelection(**{
        "status": "available",
        "studyUid": seg_instance.StudyInstanceUID,
        "seriesUid": seg_instance.SeriesInstanceUID,
        "derivedFrom": [{
          "type": "ImagingStudy",
          "identifier": {
            "system": "urn:dicom:uid",
            "value": f"urn:oid:{seg_instance.StudyInstanceUID}",
          },
        }],
        "code": {
              "coding": [ {
              "system": "https://www.cancerimagingarchive.net/collection/nsclc-radiomics/",
              "code": segment.SegmentLabel,
              "display": segment.SegmentLabel,
          }]
        },
        "instance": [{
          "uid": seg_instance.SOPInstanceUID,
          "subset": [
            segment.SegmentNumber
          ]
        }]
      })
      yield imaging_selection

imaging_selections = list(create_imaging_selections(seg_instances))

print(f"Created {len(imaging_selections)}") 
print(imaging_selections[0].json())

print("Post Imaging Selection Object to FHIR Server")
fhir_session = requests.Session()
for imaging_selection in imaging_selections:
  r = fhir_session.post("http://localhost:8080/fhir/ImagingSelection", json=imaging_selection.dict())
  r.raise_for_status()
  break #TODO remove
