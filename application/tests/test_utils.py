from __init__ import test_client
from flask import url_for
from io import BytesIO
from functools import wraps
import os
from typing import Dict, Callable


TEST_FILE_PATHS: str = [os.path.abspath(f"./test_data/example{i}.dcm") for i in range(3)]
TEST_INVALID_FILE_PATH: str = os.path.abspath("./test_data/invalid_example.dcm")

EXPECTED_HEADER_DATA: Dict[str, str] = {
    TEST_FILE_PATHS[0]: {
        '0x00080005': {
            'VR': 'CS', 
            'name': 'Specific Character Set', 
            'value': 'ISO_IR 100'
        }, 
        '0x00080008': {
            'VR': 'CS', 
            'name': 'Image Type', 
            'value': "['ORIGINAL', 'PRIMARY', 'AXIAL']"
        }, 
        '0x00080014': {
            'VR': 'UI', 
            'name': 'Instance Creator UID', 
            'value': '1.3.6.1.4.1.5962.3'
        }
    },
    TEST_FILE_PATHS[1]: {
        '0x00080005': {
            'VR': 'CS', 
            'name': 'Specific Character Set', 
            'value': 'ISO_IR 100'
        }, 
        '0x00080008': {
            'VR': 'CS', 
            'name': 'Image Type', 
            'value': "['ORIGINAL', 'PRIMARY', 'M', 'ND']"
        }
    },
    TEST_FILE_PATHS[2]: {
        '0x00080005': {
            'VR': 'CS', 
            'name': 'Specific Character Set', 
            'value': 'ISO_IR 192'
        }, 
        '0x00080008': {
            'VR': 'CS', 
            'name': 'Image Type', 
            'value': "['ORIGINAL', 'PRIMARY']"
        }
    }
}


def upload_test_file(test_client: "FlaskClient", file_path: str = TEST_FILE_PATHS[0]) -> None:
    with open(file_path, "rb") as fh:
        data = {"file": (BytesIO(fh.read()), "file.dcm")}
    return test_client.post(
        url_for("upload_file"), 
        data=data, 
        content_type="multipart/form-data",
    )


def enumerate_test_files(test_func: Callable) -> Callable:
    @wraps(test_func)
    def _wrapper(test_client: "FlaskClient", test_file_path: str) -> None:
        for file_path in TEST_FILE_PATHS:
            test_func(test_client, file_path)
    return _wrapper
