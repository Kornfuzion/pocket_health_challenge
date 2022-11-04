from . import test_client, test_file_path
import json
from test_utils import upload_test_file, enumerate_test_files, TEST_INVALID_FILE_PATH


@enumerate_test_files
def test_file_upload(test_client: "FlaskClient", test_file_path: str) -> None:
    # 1. Upload the file
    response = upload_test_file(test_client, test_file_path)
    response_data = json.loads(response.data.decode("utf-8"))

    # 2. Ensure it succeeded, returned a valid file handle
    assert "storage_handle" in response_data
    assert response.status_code == 201


def test_file_upload_wrong_file_type(test_client: "FlaskClient") -> None:
    # 1. Upload the file
    response = upload_test_file(test_client, TEST_INVALID_FILE_PATH)

    # 2. Upload fails due to incorrect file type
    assert response.status_code == 400
