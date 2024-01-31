import json
import requests
from requests.auth import HTTPBasicAuth
from dicomweb_client.api import DICOMwebClient
import dotenv
from src.utils import get_environment_variable
from pydicom.dataset import Dataset

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

# Define your username and password for Orthanc
# Load from .env file
dotenv.load_dotenv()

ORTHANC_USER = get_environment_variable("ORTHANC_USER", "admin")
ORTHANC_PW = get_environment_variable("ORTHANC_PW", "admin")


# Function to retrieve data from an endpoint
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

def retrieve_all_studies_metadata(endpoint_url,   qido_rs_endpoint = "/dicom-web/studies", auth = None):
    """
    "Retrieve all studies metadata from an QIDO-RS endpoint from Orthanc as Pydicom Datasets
    Parameters
    ----------
    endpoint_url : str
        URL of the base endpoint
    auth : requests.auth.HTTPBasicAuth
        Authentication object
    Returns
    -------
    all_datasets : list
        List of Pydicom Datasets
    """
    # Define the QIDO-RS endpoint for querying all patients
    qido_rs_endpoint = "/dicom-web/studies"

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






if __name__=='__main__':
    # Create a session
    session = requests.Session()

    # Authenticate
    session.auth = HTTPBasicAuth(ORTHANC_USER, ORTHANC_PW)

    # Define the endpoint URLs
    studies_endpoint_url = f"{ORTHANC_SERVER}/studies"
    patients_endpoint_url = f"{ORTHANC_SERVER}/patients"

    # Retrieve all study IDs
    study_ids = retrieve_data(studies_endpoint_url, auth=session.auth)
    print("Study IDs:", study_ids)

    # Retrieve all patient IDs
    patient_ids = retrieve_data(patients_endpoint_url, auth=session.auth)
    print("Patient IDs:", patient_ids)


    DICOMweb_URL = "/dicom-web/" #Root URI of the DICOMweb API (for QIDO-RS, STOW-RS and WADO-RS)
    # Initialize the DICOMwebClient with the URL of your Orthanc server
    client = DICOMwebClient(url=ORTHANC_SERVER,
                            session=session,
                            qido_url_prefix = DICOMweb_URL,
                            wado_url_prefix = DICOMweb_URL,
                            stow_url_prefix = DICOMweb_URL)  # Replace with your Orthanc server address



    # Define the QIDO-RS endpoint for querying all patients
    qido_rs_endpoint = "/dicom-web/studies"

    # Send a GET request to the QIDO-RS endpoint
    response = requests.get(ORTHANC_SERVER + qido_rs_endpoint, auth=session.auth)

    # Parse the JSON response
    json_response = response.json()

    # Extract the patient IDs from the response
    patient_ids = [dicom_metadata['0020000D']['Value'][0] for dicom_metadata in json_response]

    # Extract and print the Patient IDs
    print("Patient IDs:", patient_ids)



