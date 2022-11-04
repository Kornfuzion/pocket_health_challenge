from . import test_client
import json
from test_utils import upload_test_file


def test_get_header_attributes(test_client: "FlaskClient") -> None:
    # 1. Upload the file
    response = upload_test_file(test_client)
    response_data = json.loads(response.data.decode("utf-8"))

    # 2. Get some attributes on the DCM file by tag
    storage_handle = response_data["storage_handle"]
    tags = ["(0008,0005)", "(0008,0008)", "(0008,0014)"]
    response = test_client.get(
        f"/header_attributes/{storage_handle}",
        query_string=dict(tags=json.dumps(tags))
    )
    response_data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert response_data == {
        '(0008,0005)': {
            'VR': 'CS', 
            'name': 'Specific Character Set', 
            'value': 'ISO_IR 100'
        }, 
        '(0008,0008)': {
            'VR': 'CS', 
            'name': 'Image Type', 
            'value': "['ORIGINAL', 'PRIMARY', 'AXIAL']"
        }, 
        '(0008,0014)': {
            'VR': 'UI', 
            'name': 'Instance Creator UID', 
            'value': '1.3.6.1.4.1.5962.3'
        }
    }


def test_get_header_attributes_bad_storage_handle(test_client: "FlaskClient") -> None:
    tags = ["(0008,0005)", "(0008,0008)", "(0008,0014)"]
    response = test_client.get(
        "/header_attributes/james_xray",
        query_string=dict(tags=json.dumps(tags))
    )
    assert response.status_code == 404


def test_get_header_attributes_bad_tags(test_client: "FlaskClient") -> None:
    # 1. Upload the file
    response = upload_test_file(test_client)
    response_data = json.loads(response.data.decode("utf-8"))

    # 2. Get attributes on the DCM file by invalid tags
    storage_handle = response_data["storage_handle"]
    tags = ["(abcde,fghij)"]
    response = test_client.get(
        f"/header_attributes/{storage_handle}",
        query_string=dict(tags=json.dumps(tags))
    )
    response_data = json.loads(response.data.decode("utf-8"))

    # 3. Expect success, but no tags found
    assert response.status_code == 200
    assert response_data == {}
