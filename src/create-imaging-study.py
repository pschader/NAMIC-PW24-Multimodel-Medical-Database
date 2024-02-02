import requests

from pydicom.dataset import Dataset
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries, ImagingStudySeriesInstance

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


print("Find segmentation studies...")
studies_metadata = request('/studies')

imaging_studies = []
for study in tqdm(studies_metadata):
  series_metadata = request(f'/studies/{study.StudyInstanceUID}/series')

  imaging_study_series = []
  for series_meta in series_metadata:
    imaging_study_series_instances = []
    for instance_meta in request(f'/studies/{series_meta.StudyInstanceUID}/series/{series_meta.SeriesInstanceUID}/instances'):
      imaging_study_series_instances.append(ImagingStudySeriesInstance(
        uid=instance_meta.SOPInstanceUID,
        number=instance_meta.InstanceNumber,
        sopClass={"system": "http://dicom.nema.org/resources/ontology/DCM", "code":instance_meta.SOPClassUID}
      ))

    imaging_study_series.append(ImagingStudySeries(
      uid=series_meta.SeriesInstanceUID,
      number=series_meta.SeriesNumber,
      modality= { "coding" : [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": series_meta.Modality}]},
      instance=imaging_study_series_instances)
      )

  imaging_studies.append(ImagingStudy(
    status="available",
    subject= {
      "type": "Patient",
      "identifier": {
          "system": "https://www.cancerimagingarchive.net/collection/nsclc-radiomics/",
          "value": f"{study.PatientID}",
      },
    },
    started=study.StudyDate,
    series=imaging_study_series,
  ))
  #break

print(imaging_studies[0].json())