from . import test_client, test_file_path
import json
from test_utils import upload_test_file, enumerate_test_files, EXPECTED_HEADER_DATA


@enumerate_test_files
def test_get_header_attributes(test_client: "FlaskClient", test_file_path: str) -> None:
    # 1. Upload the file
    response = upload_test_file(test_client, test_file_path)
    response_data = json.loads(response.data.decode("utf-8"))

    # 2. Get some attributes on the DCM file by tag
    storage_handle = response_data["storage_handle"]
    tags = ["0x00080005", "0x00080008", "0x00080014"]
    response = test_client.get(
        f"/header_attributes/{storage_handle}",
        query_string=dict(tags=json.dumps(tags))
    )
    response_data = json.loads(response.data.decode("utf-8"))

    # 3. Assert success, verify response
    assert response.status_code == 200
    assert response_data == EXPECTED_HEADER_DATA[test_file_path]


def test_get_header_attributes_bad_storage_handle(test_client: "FlaskClient") -> None:
    # File not found, expect HTTP 404
    tags = ["0x00080005", "0x00080008", "0x00080014"]
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
    tags = ["invalid_tag"]
    response = test_client.get(
        f"/header_attributes/{storage_handle}",
        query_string=dict(tags=json.dumps(tags))
    )

    # 3. Bad input error
    assert response.status_code == 400
