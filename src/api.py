import json

import requests
from pydicom import dcmread, Dataset
from pathlib import Path
from pynetdicom import AE, StoragePresentationContexts
from requests.auth import HTTPBasicAuth

from src.metadata import session
from src.utils import get_environment_variable

# I
session = requests.Session()

def send_dicom_to_pacs(series_path, pacs_host, pacs_port):
    # Initialize the Application Entity
    ae = AE(ae_title='PYNETDICOM', port=2000)

    # Add a requested presentation context
    ae.requested_contexts = StoragePresentationContexts

    # Associate with peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate(pacs_host, pacs_port,  ae_title = b'ORTHANC')

    if assoc.is_established:
        print('Association Established')

        for file_path in Path(series_path).rglob('*.dcm'):

            # Read the DICOM file
            ds = dcmread(file_path)

            if assoc.is_established:
                # Use the C-STORE service to send the DICOM
                status = assoc.send_c_store(ds)

                # Check if the transmission was successful
                if status:
                    print('C-STORE request status: 0x{0:04x}'.format(status.Status))

            else:
                print('Association rejected, aborted or never connected')

        # Release the association
        assoc.release()

if __name__=='__main__':

    # Define the host and port of the PACS
    pacs_host = 'localhosts'
    pacs_port = 4242

    # Define the path to the DICOM file
    file_path = '/Users/mmonzon/Downloads/TCIA/manifest-1603198545583/NSCLC-Radiomics/LUNG1-006/1.3.6.1.4.1.32722.99.99.270361505197008655909592732352678399263'

    # Send the DICOM file to the PACS
    send_dicom_to_pacs(file_path, pacs_host, pacs_port)
ORTHANC_SERVER = "http://localhost:8042"
DICOM_TAGS = {
    "PatientID": "00100020",
    "PatientName": "00100010",
    "PatientBirthDate": "00100030",
    "PatientSex": "00100040",
    # Study level tags
    "StudyInstanceUID": "0020000D",
    "StudyDate": "00080020",
    "StudyTime": "00080030",
    "StudyDescription": "00081030",
    "StudyID": "00200010",
    "AccessionNumber": "00080050",
    "Modality": "00080060",
    "Manufacturer": "00080070",
    "InstitutionName": "00080080",

    # Series level tags
    "SeriesInstanceUID": "0020000E",
    "SeriesDescription": "0008103E",
    "SeriesNumber": "00200011",
    "BodyPartExamined": "00180015",
    "ProtocolName": "00181030",
    "PatientPosition": "00185100",
    "PixelSpacing": "00280030",
    "Rows": "00280010",
    "Columns": "00280011",
    "PixelRepresentation": "00280103",
    "WindowCenter": "00281050",
    "WindowWidth": "00281051",
    "RescaleIntercept": "00281052",
    "RescaleSlope": "00281053",

    # Instance level tags
    "InstanceNumber": "00200013",
    "SOPInstanceUID": "00080018",
    "SOPClassUID": "00080016",
    "InstanceCreationDate": "00080012",
    "InstanceCreationTime": "00080013",
    "ImageType": "00080008",
    # Other tags
    "AcquisitionNumber": "00200012",
    "AcquisitionDate": "00080022",
    "AcquisitionTime": "00080032",
    "AcquisitionDateTime": "0008002A",
    "ContentDate": "00080023",
    "ContentTime": "00080033",
    "ContentDateTime": "00080023",
    "SeriesDate": "00080021",
    "SeriesTime": "00080031",
    "PerformedProcedureStepStartDate": "00400244",
    "PerformedProcedureStepStartTime": "00400245",
}
ORTHANC_USER = get_environment_variable("ORTHANC_USER", "admin")
ORTHANC_PW = get_environment_variable("ORTHANC_PW", "admin")


def retrieve_data(endpoint_url, auth = None):

    # Send a GET request to the endpoint
    response = requests.get(endpoint_url, auth = auth)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        metadata = json.loads(response.text)
        return metadata
    else:
        print(f"Error: {response.status_code}")
        return None


def retrieve_all_studies_metadata(endpoint_url,  qido_rs_endpoint = "/dicom-web/studies", auth = None):
    """
    "Retrieve all studies metadata from an QIDO-RS endpoint from Orthanc as Pydicom Datasets
    Parameters
    ----------
    endpoint_url : str
        URL of the base endpoint
    qido_rs_endpoint
        QIDO-RS endpoint
    auth : requests.auth.HTTPBasicAuth
        Authentication object
    Returns
    -------
    all_datasets : list
        List of Pydicom Datasets
    """

    studies_metadata = retrieve_data(endpoint_url + qido_rs_endpoint, auth = auth)
    all_datasets = []
    if studies_metadata is not None:
        all_datasets = [Dataset.from_json(study) for study in studies_metadata]
    return all_datasets


def get_patients_ids(qido_rs_endpoint, auth = None):

    # Send a GET request to the QIDO-RS endpoint
    response = requests.get(qido_rs_endpoint, auth = auth)

    # Extract and print the Patient IDs
    if response.status_code == 200:
        patients = response.json()
        patient_ids = [patient['00100020']['Value'][0] for patient in patients]
        return patient_ids

    else:
        print(f"Error: {response.status_code}")
        return None


def test_orthanc():
    # Authenticate
    session.auth = HTTPBasicAuth(ORTHANC_USER, ORTHANC_PW)
    # Define the endpoint URLs
    studies_endpoint_url = f"{ORTHANC_SERVER}/studies"
    patients_endpoint_url = f"{ORTHANC_SERVER}/patients"
    # Retrieve all study IDs of ORTHANC
    study_ids = retrieve_data(studies_endpoint_url, auth=session.auth)
    print("Study IDs in ORTHANC:", study_ids)
    # Define the QIDO-RS endpoint for querying all patients
    qido_rs_endpoint = "/dicom-web/studies"
    wado_rs_endpoint = "/dicom-web/wado"
    # Send a GET request to the QIDO-RS endpoint
    response = requests.get(ORTHANC_SERVER + qido_rs_endpoint, auth=session.auth)
    # Parse the JSON response
    json_response = response.json()
    # Extract the patient IDs from the response
    patient_ids = [dicom_metadata[DICOM_TAGS['PatientID']]['Value'][0] for dicom_metadata in json_response]
    patient_ids = [dicom_metadata.get(DICOM_TAGS['StudyID']) for dicom_metadata in json_response]
    # Extract and print the Patient IDs
    print("Patient IDs:", patient_ids)
