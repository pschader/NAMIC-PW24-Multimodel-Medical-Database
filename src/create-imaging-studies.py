import requests
from pydicom.dataset import Dataset
from requests.auth import HTTPBasicAuth

headers = {
  'Accept': 'application/dicom+json'
}

auth = HTTPBasicAuth('admin', 'admin')
response = requests.get('http://localhost:8042/dicom-web/studies', auth=auth, headers=headers)
response.raise_for_status()

objs = []
for x in response.json():
  objs.append(Dataset.from_json(x))

print(len(objs))