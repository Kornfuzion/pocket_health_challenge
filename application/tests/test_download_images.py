from . import test_client, test_file_path
import json
from test_utils import upload_test_file, enumerate_test_files


@enumerate_test_files
def test_image_file_download(test_client: "FlaskClient", test_file_path: str) -> None:
    # 1. Upload the file
    response = upload_test_file(test_client, test_file_path)
    response_data = json.loads(response.data.decode("utf-8"))

    # 2. Read the file using the storage handle
    storage_handle = response_data["storage_handle"]
    response = test_client.get(f"/uploads/image/{storage_handle}")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == f"inline; filename={storage_handle}.png"
    assert response.headers["Content-Type"] == "image/png"


def test_image_file_download_bad_handle(test_client: "FlaskClient") -> None:
    # 1. Read non-existent file
    response = test_client.get("/uploads/image/james_xray")
    
    # 2. Ensure 404 due to not found
    assert response.status_code == 404
