from . import test_client
import json
from test_utils import upload_test_file


def test_dicom_file_download(test_client: "FlaskClient") -> None:
    # 1. Upload the file
    response = upload_test_file(test_client)
    response_data = json.loads(response.data.decode("utf-8"))

    # 2. Read the file using the storage handle
    storage_handle = response_data["storage_handle"]
    response = test_client.get(f"/uploads/dicom/{storage_handle}")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == f"inline; filename={storage_handle}.dcm"
    assert response.headers["Content-Type"] == "application/octet-stream"


def test_dicom_file_download_bad_handle(test_client: "FlaskClient") -> None:
    # 1. Read non-existent file
    response = test_client.get("/uploads/dicom/james_xray")
    
    # 2. Ensure 404 due to not found
    assert response.status_code == 404
