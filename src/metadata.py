import json
import requests
import dotenv
from pydicom import dcmread
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries, ImagingStudySeriesInstance

from datetime import datetime
from collections import OrderedDict

# Define a custom encoder to handle non-serializable objects
class FHIREncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, OrderedDict):
            return dict(o)


# Define your username and password for Orthanc
# Load from .env file
dotenv.load_dotenv()


# Function to retrieve data from an endpoint


def dicom_to_fhir(dicom_dir):

    dicom_series = get_dicom_paths(dicom_dir)

    for suid, fpaths in dicom_series.items():
        # Read the DICOM file
        series = [dcmread(str(f)) for f in fpaths]
        ds = series[0]

        imaging_study = ImagingStudy(
            id=ds.StudyInstanceUID,
            status="available",
            subject={"reference": f"Patient/{ds.PatientID}"},
            started=ds.StudyDate,
            series=[
                ImagingStudySeries(
                    uid=s.SeriesInstanceUID,
                    number=s.SeriesNumber,
                    modality= { "coding" : [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": s.Modality}]},
                    instance=[
                        ImagingStudySeriesInstance(
                            uid=instance.SOPInstanceUID,
                            number=instance.InstanceNumber,
                            sopClass={"system": "http://dicom.nema.org/resources/ontology/DCM", "code":instance.SOPClassUID}
                        )
                        for instance in series
                    ]
                )
                for s in series
            ]
        )

    return imaging_study


def get_dicom_paths(data_directory):
    # Create an ImageSeriesReader object
    reader = sitk.ImageSeriesReader()
    dcm_paths = {}

    # get the Series UIDs of the DICOM files
    series_IDs = []
    dicomdirs = np.unique([str(f.parent) for f in Path(dicom_dir).rglob('*.dcm')])

    for dirpath in dicomdirs:
        # Use SimpleITK to get the series IDs in the current directory
        current_series_ids = reader.GetGDCMSeriesIDs(str(dirpath))

        # If there are series IDs found, extend the main list
        if current_series_ids:
            for suid in current_series_ids:
                dcm_paths[suid] = reader.GetGDCMSeriesFileNames(str(dirpath), suid)
            series_IDs.extend(current_series_ids)

    return dcm_paths


if __name__=='__main__':
    # Create a session
    session = requests.Session()
    # test_orthanc()


    # Define the path to the DICOM file
    dicom_dir = '/Users/mmonzon/Downloads/TCIA/manifest-1603198545583/NSCLC-Radiomics/LUNG1-006/'

    # Create the FHIR ImagingStudy object
    imaging_study = dicom_to_fhir(dicom_dir)